# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, formatdate, cstr, rounded, get_first_day, get_last_day
from frappe import _
from erpnext.accounts.utils import get_account_currency
from datetime import datetime, timedelta
from collections import OrderedDict
#changes
def execute(filters=None):
	month_id = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}[filters.month]
	dates = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=False)
	start, end = [datetime.strptime(str(i), "%Y-%m-%d") for i in dates]
	# year_start_date = frappe.db.get_value("Fiscal Year", filters.fiscal_year,["year_start_date"])
	months = OrderedDict(((start + timedelta(i)).strftime(r"%Y-%m"), None) for i in xrange((end - start).days)).keys()
	actual_date = [i for i in months if i[-2:] == month_id][0] + "-01"
	from_date = get_first_day(actual_date)
	to_date = get_last_day(actual_date)
	account_details = {}
	for acc in frappe.db.sql("""select name, is_group from tabAccount""", as_dict=1):
		account_details.setdefault(acc.name, acc)

	validate_filters(filters, account_details)

	validate_party(filters)

	filters = set_account_currency(filters)

	columns = get_columns(filters)

	res = get_result(filters, account_details, from_date, to_date)

	return columns, res

def validate_filters(filters, account_details):
	if not filters.get('company'):
		frappe.throw(_('{0} is mandatory').format(_('Company')))

	if filters.get("account") and not account_details.get(filters.account):
		frappe.throw(_("Account {0} does not exists").format(filters.account))

	if filters.get("account") and filters.get("group_by_account") \
			and account_details[filters.account].is_group == 0:
		frappe.throw(_("Can not filter based on Account, if grouped by Account"))

	if filters.get("voucher_no") and filters.get("group_by_voucher"):
		frappe.throw(_("Can not filter based on Voucher No, if grouped by Voucher"))

	# if filters.from_date > filters.to_date:
	# 	frappe.throw(_("From Date must be before To Date"))


def validate_party(filters):
	party_type, party = filters.get("party_type"), filters.get("party")

	if party:
		if not party_type:
			frappe.throw(_("To filter based on Party, select Party Type first"))
		elif not frappe.db.exists(party_type, party):
			frappe.throw(_("Invalid {0}: {1}").format(party_type, party))

def set_account_currency(filters):
	if not (filters.get("account") or filters.get("party")):
		return filters
	else:
		filters["company_currency"] = frappe.db.get_value("Company", filters.company, "default_currency")
		account_currency = None

		if filters.get("account"):
			account_currency = get_account_currency(filters.account)
		elif filters.get("party"):
			gle_currency = frappe.db.get_value("GL Entry", {"party_type": filters.party_type,
				"party": filters.party, "company": filters.company}, "account_currency")
			if gle_currency:
				account_currency = gle_currency
			else:
				if filters.party_type!="Employee":
					account_currency = frappe.db.get_value(filters.party_type, filters.party, "default_currency")

		filters["account_currency"] = account_currency or filters.company_currency

		if filters.account_currency != filters.company_currency:
			filters["show_in_account_currency"] = 1

		return filters

def get_columns(filters):
	columns = [
		_("Date") + ":Date:90", _("Particulars") + ":Link/Account:200",
		_("Debit") + ":Float:100", _("Credit") + ":Float:100"
	]

	if filters.get("show_in_account_currency"):
		columns += [
			_("Debit") + " (" + filters.account_currency + ")" + ":Float:100",
			_("Credit") + " (" + filters.account_currency + ")" + ":Float:100"
		]

	columns += [
		_("Voucher Type") + "::120", _("Voucher No") + ":Dynamic Link/"+_("Voucher Type")+":160",
		_("Against Account") + "::180", _("Cheque No") + "::120", _("Party Type") + "::80", _("Party") + "::150",
		_("Cost Center") + ":Link/Cost Center:120", _("Funding Pool") + ":Link/Business Activity:120",
		_("Remarks") + "::400"
	]

	return columns

def get_result(filters, account_details, from_date, to_date):
	gl_entries = get_gl_entries(filters, from_date)

	data = get_data_with_opening_closing(filters, account_details, gl_entries, from_date, to_date)

	result = get_result_as_list(data, filters)

	return result

def get_gl_entries(filters, from_date):
	select_fields = """, sum(debit_in_account_currency) as debit_in_account_currency,
		sum(credit_in_account_currency) as credit_in_account_currency""" \
		if filters.get("show_in_account_currency") else ""

	group_by_condition = "group by a.voucher_type, a.voucher_no, a.account, a.cost_center" \
		if filters.get("group_by_voucher") else "group by name"

	gl_entries = frappe.db.sql("""
		select
			a.posting_date, a.account, a.party_type, a.party,
			sum(a.debit) as debit, sum(a.credit) as credit,
			a.voucher_type, a.voucher_no, a.cost_center, a.business_activity,
			a.remarks, CASE WHEN a.voucher_type = "Journal Entry" THEN (select GROUP_CONCAT(DISTINCT(jea.account) SEPARATOR ',') as account from `tabJournal Entry Account` jea where jea.parent = a.voucher_no and jea.account != a.account) WHEN a.voucher_type = 'Direct Payment' THEN (select dp.debit_account from `tabDirect Payment` dp where dp.name = a.voucher_no)
			WHEN a.voucher_type = "TDS Remittance" THEN (select tdr.tds_account from `tabTDS Remittance` tdr where tdr.name = a.voucher_no) END as against,
			CASE WHEN a.voucher_type = "Journal Entry" THEN (select je.cheque_no from `tabJournal Entry` je where je.name = a.voucher_no) WHEN a.voucher_type = 'Direct Payment' THEN (select dp.cheque_no from `tabDirect Payment` dp where dp.name = a.voucher_no)
			WHEN a.voucher_type = "TDS Remittance" THEN (select tdr.cheque_no from `tabTDS Remittance` tdr where tdr.name = a.voucher_no) END as cheque_no,
			a.is_opening {select_fields}
		from `tabGL Entry` a
		where a.docstatus = 1 and a.account in ('80.02-CD AC 101214282 - GCC','80.01-Cash in Hand - GCC') and a.company=%(company)s {conditions}
		{group_by_condition}
		order by a.posting_date, a.account"""\
		.format(select_fields=select_fields, conditions=get_conditions(filters, from_date),
			group_by_condition=group_by_condition), filters, as_dict=1)

	return gl_entries

def get_conditions(filters, from_date):
	conditions = []
	if filters.get("account"):
		lft, rgt = frappe.db.get_value("Account", filters["account"], ["lft", "rgt"])
		conditions.append("""a.account in (select name from tabAccount
			where lft>=%s and rgt<=%s and docstatus<2)""" % (lft, rgt))

	if filters.get("voucher_no"):
		conditions.append("a.voucher_no=%(voucher_no)s")

	if filters.get("cost_center"):
		conditions.append("a.cost_center=%(cost_center)s")

	if filters.get("party_type"):
		conditions.append("a.party_type=%(party_type)s")

	if filters.get("party"):
		conditions.append("a.party=%(party)s")

	if not (filters.get("account") or filters.get("party") or filters.get("group_by_account")):
		conditions.append("a.posting_date >='{0}'".format(from_date))
	#added filters for Business Activity
	if filters.get("business_activity"):
		conditions.append("a.business_activity = %(business_activity)s")

	from frappe.desk.reportview import build_match_conditions
	match_conditions = build_match_conditions("GL Entry")
	if match_conditions: conditions.append(match_conditions)

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_data_with_opening_closing(filters, account_details, gl_entries, from_date, to_date):
	data = []
	gle_map = initialize_gle_map(gl_entries)

	opening, total_debit, total_credit, opening_in_account_currency, total_debit_in_account_currency, \
		total_credit_in_account_currency, gle_map = get_accountwise_gle(filters, gl_entries, gle_map, from_date, to_date)

	# Opening for filtered account
	if filters.get("account") or filters.get("party"):
		data += [get_balance_row(_("Opening"), opening, opening_in_account_currency), {}]

	if filters.get("group_by_account"):
		for acc, acc_dict in gle_map.items():
			if acc_dict.entries:
				# Opening for individual ledger, if grouped by account
				data.append(get_balance_row(_("Opening"), acc_dict.opening,
					acc_dict.opening_in_account_currency))

				data += acc_dict.entries

				# Totals and closing for individual ledger, if grouped by account
				account_closing = acc_dict.opening + acc_dict.total_debit - acc_dict.total_credit
				account_closing_in_account_currency = acc_dict.opening_in_account_currency \
					+ acc_dict.total_debit_in_account_currency - acc_dict.total_credit_in_account_currency

				data += [{"account": _("Totals"), "debit": acc_dict.total_debit,
					"credit": acc_dict.total_credit},
					get_balance_row(_("Closing"),
						account_closing, account_closing_in_account_currency), {}]

	else:
		for gl in gl_entries:
			if gl.posting_date >= getdate(from_date) and gl.posting_date <= getdate(to_date) \
					and gl.is_opening == "No":
				data.append(gl)


	# Total debit and credit between from and to date
	if total_debit or total_credit:
		data.append({
			"account": _("Totals"),
			"debit": total_debit,
			"credit": total_credit,
			"debit_in_account_currency": total_debit_in_account_currency,
			"credit_in_account_currency": total_credit_in_account_currency
		})

	# Closing for filtered account
	if filters.get("account") or filters.get("party"):
		closing = opening + total_debit - total_credit
		closing_in_account_currency = opening_in_account_currency + \
			total_debit_in_account_currency - total_credit_in_account_currency

		data.append(get_balance_row(_("Closing"),
			closing, closing_in_account_currency))

	return data

def initialize_gle_map(gl_entries):
	gle_map = frappe._dict()
	for gle in gl_entries:
		gle_map.setdefault(gle.account, frappe._dict({
			"opening": 0,
			"opening_in_account_currency": 0,
			"entries": [],
			"total_debit": 0,
			"total_debit_in_account_currency": 0,
			"total_credit": 0,
			"total_credit_in_account_currency": 0,
			"closing": 0,
			"closing_in_account_currency": 0
		}))
	return gle_map

def get_accountwise_gle(filters, gl_entries, gle_map, from_date, to_date):
	opening, total_debit, total_credit = 0, 0, 0
	opening_in_account_currency, total_debit_in_account_currency, total_credit_in_account_currency = 0, 0, 0

	from_date, to_date = getdate(from_date), getdate(to_date)
	for gle in gl_entries:
		amount = flt(gle.debit, 3) - flt(gle.credit, 3)
		amount_in_account_currency = flt(gle.debit_in_account_currency, 3) - flt(gle.credit_in_account_currency, 3)

		if (filters.get("account") or filters.get("party") or filters.get("group_by_account")) \
				and (gle.posting_date < from_date or cstr(gle.is_opening) == "Yes"):

			gle_map[gle.account].opening += amount
			if filters.get("show_in_account_currency"):
				gle_map[gle.account].opening_in_account_currency += amount_in_account_currency

			if filters.get("account") or filters.get("party"):
				opening += amount
				if filters.get("show_in_account_currency"):
					opening_in_account_currency += amount_in_account_currency

		elif gle.posting_date <= to_date:
			gle_map[gle.account].entries.append(gle)
			gle_map[gle.account].total_debit += flt(gle.debit, 3)
			gle_map[gle.account].total_credit += flt(gle.credit, 3)

			total_debit += flt(gle.debit, 3)
			total_credit += flt(gle.credit, 3)

			if filters.get("show_in_account_currency"):
				gle_map[gle.account].total_debit_in_account_currency += flt(gle.debit_in_account_currency, 3)
				gle_map[gle.account].total_credit_in_account_currency += flt(gle.credit_in_account_currency, 3)

				total_debit_in_account_currency += flt(gle.debit_in_account_currency, 3)
				total_credit_in_account_currency += flt(gle.credit_in_account_currency, 3)

	return opening, total_debit, total_credit, opening_in_account_currency, \
		total_debit_in_account_currency, total_credit_in_account_currency, gle_map

def get_balance_row(label, balance, balance_in_account_currency=None):
	balance_row = {
		"account": label,
		"debit": balance if balance > 0 else 0,
		"credit": -1*balance if balance < 0 else 0
	}

	if balance_in_account_currency != None:
		balance_row.update({
			"debit_in_account_currency": balance_in_account_currency if balance_in_account_currency > 0 else 0,
			"credit_in_account_currency": -1*balance_in_account_currency if balance_in_account_currency < 0 else 0
		})

	return balance_row

def get_result_as_list(data, filters):
	result = []
	for d in data:
		row = [d.get("posting_date"), d.get("account"), d.get("debit"), flt(d.get("credit"))]

		if filters.get("show_in_account_currency"):
			row += [d.get("debit_in_account_currency"), d.get("credit_in_account_currency")]

		row += [d.get("voucher_type"), d.get("voucher_no"), d.get("against"), d.get("cheque_no"),
			d.get("party_type"), d.get("party"), d.get("cost_center"), d.get("business_activity"), d.get("remarks")
		]

		result.append(row)

	return result
