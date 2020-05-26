# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, rounded
from erpnext.accounts.report.financial_statements_gyalsung \
	import filter_accounts, set_gl_entries_by_account, filter_out_zero_value_rows
from erpnext.accounts.accounts_custom_functions import get_child_cost_centers

value_fields = ("opening_debit", "opening_credit", "debit", "credit", "closing_debit", "closing_credit")

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_data(filters):
	validate_filters(filters)
        data   		= []
	debit, credit, total_debit, total_credit = 0, 0, 0, 0

	base_gl = frappe.db.sql_list("select name from `tabAccount` where account_type in ('Bank', 'Cash')")
	accounts, accounts_by_name = get_accounts()

	for report_head in ["Opening Cash or Bank", "Receipt", "Payment", "Closing Cash or Bank"]:
		# level-1 heading
		data += [frappe._dict({
			'account': report_head, 'account_name': report_head, 'account_code': None, 'parent_account': None, 
			'indent': 0, 'debit': 0, 'credit': 0, 
		})]

		# get the values
		formatted, debit, credit = get_gl_totals(filters, base_gl, report_head, accounts_by_name)
		data += formatted
		total_debit  += flt(debit)
		total_credit += flt(credit)

	# total row
#	data += [frappe._dict({
#		'account': 'Total', 'account_name': 'Total', 'account_code': None, 'parent_account': None, 
#		'indent': 0, 'debit': total_debit, 'credit': total_credit, 
#	})]

        return data

def get_accounts():
	accounts = frappe.db.sql("""select name as account, account_code, account_name, lft, rgt 
			from `tabAccount` order by lft, rgt""", as_dict=True)
	accounts_by_name = frappe._dict()
	for i in accounts:
		accounts_by_name[i.account] = i

	return accounts, accounts_by_name

def get_gl_totals(filters, base_gl, report_head, accounts_by_name):
	base_gl = tuple(str(i) for i in base_gl)
	formatted = []
	total_debit, total_credit = 0, 0

	columns, cond = get_columns_and_conditions(filters, base_gl, report_head)
	report_head_id= str(report_head).lower().replace(' ','_')
	data 	= frappe.db.sql("""
		select 
			(case when parent_account is null then 1 else -1 end) order_by,
			'{report_head}' report_head,
			gl1.account,
			concat(gl1.account,'{report_head_id}') account_id,
			a.account_name,
			a.account_code,
			a.parent_account,
			concat(a.parent_account,'{report_head_id}') parent_account_id,
			1 as indent,
			{columns}
		from `tabGL Entry` gl1, `tabAccount` a
		{cond}
		and a.name = gl1.account
		group by order_by, report_head, gl1.account, concat(gl1.account,'{report_head_id}'), 
			a.account_name, a.account_code, a.parent_account, concat(a.parent_account,'{report_head_id}')
		order by order_by, a.parent_account, gl1.account
	""".format(report_head=report_head, report_head_id=report_head_id, columns=columns, cond=cond), as_dict=True)

	formatted, total_debit, total_credit = get_formatted(data, accounts_by_name)
	return formatted, total_debit, total_credit 

def get_formatted(data, accounts_by_name):
	formatted = []
	total_debit, total_credit = 0, 0
	prev_parent = ""
	for i in data:
		indent = 1
		if i.parent_account:
			if prev_parent != i.parent_account:
				# level-2 heading
				formatted += [frappe._dict({
					'account': i.parent_account, 'account_name': accounts_by_name[i.parent_account].account_name, 
					'account_code': None, 'parent_account': i.report_head, 
					'indent': indent, 'debit': 0, 'credit': 0, 
				})]
			indent += 1
			prev_parent = i.parent_account
		else:
			prev_parent = i.report_head

		# level-3
		formatted += [frappe._dict({
			'account': i.account, 'account_name': i.account_name, 
			'account_code': i.account_code, 'parent_account': prev_parent, 
			'indent': indent, 'debit': i.debit, 'credit': i.credit, 
		})]
		total_debit  += flt(i.debit)
		total_credit += flt(i.credit)
	return formatted, total_debit, total_credit 

def get_columns_and_conditions(filters, base_gl, report_head):
	cond = ""	
	if report_head == "Receipt":
		columns = "sum(gl1.credit) as debit, 0 as credit"
		cond 	= """where gl1.posting_date between '{}' and '{}' 
				and exists(select 1
					from `tabGL Entry` gl2
					where gl2.voucher_type = gl1.voucher_type
					and gl2.voucher_no = gl1.voucher_no
					and gl2.account in {}
					and ifnull(gl2.debit,0) > 0
				)
				and gl1.account not in {}
		""".format(filters.from_date, filters.to_date, base_gl, base_gl)
	elif report_head == "Payment":
		columns = "0 as debit, sum(gl1.debit) as credit"
		cond 	= """where gl1.posting_date between '{}' and '{}' 
				and exists(select 1
					from `tabGL Entry` gl2
					where gl2.voucher_type = gl1.voucher_type
					and gl2.voucher_no = gl1.voucher_no
					and gl2.account in {}
					and ifnull(gl2.credit,0) > 0
				)
				and gl1.account not in {}
		""".format(filters.from_date, filters.to_date, base_gl, base_gl)
	elif report_head == "Opening Cash or Bank":
		columns = "sum(gl1.debit) as debit, sum(gl1.credit) as credit"
		cond 	= """where gl1.posting_date < '{}'
				and gl1.account in {}
		""".format(filters.from_date, base_gl)
	else:
		#columns ="(sum(gl1.debit)+ sum(gl1.credit) - sum(gl1.debit)) as debit, 0 as credit"
		columns = "sum(gl1.debit) as debit, sum(gl1.credit) as credit"
		cond = """where gl1.posting_date <= '{}'
				and gl1.account in {}
		""".format(filters.to_date, base_gl)
	return columns, cond

def get_rootwise_opening_balances(filters, report_type):
	additional_conditions = " and posting_date >= %(year_start_date)s" \
		if report_type == "Profit and Loss" else ""

	if not flt(filters.with_period_closing_entry):
		additional_conditions += " and ifnull(voucher_type, '')!='Period Closing Voucher'"

        if filters.cost_center:
		cost_centers = get_child_cost_centers(filters.cost_center)
                additional_conditions += " and cost_center IN %(cost_center)s"
        else:
		cost_centers = filters.cost_center 
	gle = frappe.db.sql("""
		select
			account, sum(debit) as opening_debit, sum(credit) as opening_credit	
			from `tabGL Entry` 
			where voucher_no in ( select voucher_no from `tabGL Entry` where account
 			in (select name from `tabAccount` where account_type in ('Bank', 'Cash'))) and 
			company=%(company)s 
			{additional_conditions}
			and (posting_date < %(from_date)s or ifnull(is_opening, 'No') = 'Yes')
		group by account""".format(additional_conditions=additional_conditions),
		{
			"company": filters.company,
			"from_date": filters.from_date,
			"year_start_date": filters.year_start_date,
                        "cost_center": cost_centers
		},
		as_dict=True)

	opening = frappe._dict()
	for d in gle:
		opening.setdefault(d.account, d)

	return opening

def validate_filters(filters):
	if not filters.fiscal_year:
		frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

	fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
	if not fiscal_year:
		frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
	else:
		filters.year_start_date = getdate(fiscal_year.year_start_date)
		filters.year_end_date = getdate(fiscal_year.year_end_date)

	if not filters.from_date:
		filters.from_date = filters.year_start_date

	if not filters.to_date:
		filters.to_date = filters.year_end_date

	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

	if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
		frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
			.format(formatdate(filters.year_start_date)))

		filters.from_date = filters.year_start_date

	if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
		frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
			.format(formatdate(filters.year_end_date)))
		filters.to_date = filters.year_end_date

def get_columns():
	return [
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 350
		},
		{
			"fieldname": "account_code",
			"label": _("Account Code"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "debit",
			"label": _("Debit"),
			"fieldtype": "Currency",
			"width": 180
		},
		{
			"fieldname": "credit",
			"label": _("Credit"),
			"fieldtype": "Currency",
			"width": 180
		},
	]


