# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
#Modified by Kinley Tshering (kinleytshering@dhi.bt) for cost_center filter

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import (flt, getdate, get_first_day, get_last_day,
	add_months, add_days, formatdate)
from erpnext.accounts.accounts_custom_functions import get_child_cost_centers
from datetime import datetime, timedelta
from collections import OrderedDict

def get_period_list(fiscal_year, periodicity):
	"""Get a list of dict {"from_date": from_date, "to_date": to_date, "key": key, "label": label}
		Periodicity can be (Yearly, Quarterly, Monthly)"""

	fy_start_end_date = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"])
	if not fy_start_end_date:
		frappe.throw(_("Fiscal Year {0} not found.").format(fiscal_year))

	# start with first day, so as to avoid year to_dates like 2-April if ever they occur]
	year_start_date = get_first_day(getdate(fy_start_end_date[0]))
	year_end_date = getdate(fy_start_end_date[1])

	if periodicity == "Yearly":
		period_list = [frappe._dict({"from_date": year_start_date, "to_date": year_end_date,
			"key": fiscal_year, "label": fiscal_year})]
		
	elif periodicity in ('Monthly', 'Quarterly', 'Half-Yearly'):
		months_to_add = {
			"Half-Yearly": 6,
			"Quarterly": 3,
			"Monthly": 1
		}[periodicity]

		period_list = []

		start_date = year_start_date
		for i in xrange(12 / months_to_add):
			period = frappe._dict({
				"from_date": start_date
			})
			to_date = add_months(start_date, months_to_add)
			start_date = to_date

			if to_date == get_first_day(to_date):
				# if to_date is the first day, get the last day of previous month
				to_date = add_days(to_date, -1)
			else:
				# to_date should be the last day of the new to_date's month
				to_date = get_last_day(to_date)

			if to_date <= year_end_date:
				# the normal case
				period.to_date = to_date
			else:
				# if a fiscal year ends before a 12 month period
				period.to_date = year_end_date

			period_list.append(period)

			if period.to_date == year_end_date:
				break
	else:
		period_list = []
		dates = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"], as_dict=False)
		start, end = [datetime.strptime(str(i), "%Y-%m-%d") for i in dates]
		months = OrderedDict(((start + timedelta(i)).strftime(r"%Y-%m"), None) for i in xrange((end - start).days)).keys()
		actual_date = [i for i in months if i[-2:] == periodicity][0] + "-01"
		month_start = get_first_day(actual_date)
		month_end = get_last_day(actual_date)
		period = frappe._dict({
				"from_date": month_start,
				"to_date": month_end
			})
		period_list.append(period)
		

	# common processing
	for opts in period_list:
		key = opts["to_date"].strftime("%b_%Y").lower()
		if periodicity == "Monthly":
			label = formatdate(opts["to_date"], "MMM YYYY")
		else:
			label = get_label(periodicity, opts["from_date"], opts["to_date"])

		opts.update({
			"key": key.replace(" ", "_").replace("-", "_"),
			"label": label,
			"year_start_date": year_start_date,
			"year_end_date": year_end_date
		})

	return period_list

def get_label(periodicity, from_date, to_date):
	if periodicity=="Yearly":
		if formatdate(from_date, "YYYY") == formatdate(to_date, "YYYY"):
			label = formatdate(from_date, "YYYY")
		else:
			label = formatdate(from_date, "YYYY") + "-" + formatdate(to_date, "YYYY")
	else:
		label = formatdate(from_date, "MMM YY") + "-" + formatdate(to_date, "MMM YY")

	return label

def get_data(cost_center, business_activity, company, root_type, balance_must_be, exclude, period_list,
		accumulated_values=1, only_current_fiscal_year=True, ignore_closing_entries=False, show_zero_values=False, periodicity = None):
	accounts = get_accounts(company, exclude, root_type)
	if not accounts:
		return None

	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

	company_currency = frappe.db.get_value("Company", company, "default_currency")
	gl_entries_by_account = {}
	for root in frappe.db.sql("""select lft, rgt from tabAccount
			where root_type=%s and ifnull(parent_account, '') = ''""", root_type, as_dict=1):
	

		set_gl_entries_by_account(cost_center, business_activity, company,
			period_list[0]["year_start_date"] if only_current_fiscal_year else None,
			period_list[-1]["to_date"],
			root.lft, root.rgt,
			gl_entries_by_account, ignore_closing_entries=ignore_closing_entries)

	calculate_values(accounts_by_name, gl_entries_by_account, period_list, accumulated_values)
	accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values)
	out = prepare_data(fiscal_year, cost_center, accounts, balance_must_be, period_list, company_currency)
	#frappe.msgprint("out: {}".format(out))
	out = filter_out_zero_value_rows(out, parent_children_map, show_zero_values)

	if out:
		add_total_row(out, root_type, balance_must_be, period_list, company_currency)

	return out

def get_data_es(fiscal_year, cost_center, business_activity, company, root_type, balance_must_be, exclude, period_list,
		accumulated_values=1, only_current_fiscal_year=True, ignore_closing_entries=False, show_zero_values=False, periodicity = None):
	accounts = get_accounts(company, exclude, root_type)
	total = 0
	if not accounts:
		return None

	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

	company_currency = frappe.db.get_value("Company", company, "default_currency")
	gl_entries_by_account = {}
	for root in frappe.db.sql("""select lft, rgt from tabAccount
			where root_type=%s and ifnull(parent_account, '') = ''""", root_type, as_dict=1):
		set_gl_entries_by_account(cost_center, business_activity, company,
			period_list[0]["year_start_date"] if only_current_fiscal_year else None,
			period_list[-1]["to_date"],
			root.lft, root.rgt,
			gl_entries_by_account, ignore_closing_entries=ignore_closing_entries)
	# frappe.throw(str(gl_entries_by_account))

	calculate_values(accounts_by_name, gl_entries_by_account, period_list, accumulated_values)
	accumulate_values_into_parents_es(accounts, accounts_by_name, period_list, accumulated_values)
	out = prepare_data_es(periodicity, fiscal_year, cost_center, business_activity, accounts, balance_must_be, period_list, company_currency)
	#frappe.msgprint("out: {}".format(out))
	out, budget, progressive= filter_out_zero_value_rows_es(period_list, business_activity, out, parent_children_map, show_zero_values)
	
	# if root_type == "Asset":
	# 	frappe.msgprint(str(out))

	if out:
		total = add_total_row_es(out, balance_must_be, period_list, company_currency)

	return out, total, budget, progressive

def calculate_values(accounts_by_name, gl_entries_by_account, period_list, accumulated_values):
	for entries in gl_entries_by_account.values():
		for entry in entries:
			d = accounts_by_name.get(entry.account)
			if d != None:
				for period in period_list:
					# check if posting date is within the period
					if entry.posting_date <= period.to_date:
						if accumulated_values or entry.posting_date >= period.from_date:
							d[period.key] = d.get(period.key, 0.0) + flt(entry.debit) - flt(entry.credit)
				if entry.posting_date < period_list[0].year_start_date:
					d["opening_balance"] = d.get("opening_balance", 0.0) + flt(entry.debit) - flt(entry.credit)

def accumulate_values_into_parents(accounts, accounts_by_name, period_list, accumulated_values):
	"""accumulate children's values in parent accounts"""
	for d in reversed(accounts):
		
		if d.parent_account:
			for period in period_list:
				accounts_by_name[d.parent_account][period.key] = \
					accounts_by_name[d.parent_account].get(period.key, 0.0) + d.get(period.key, 0.0)

			accounts_by_name[d.parent_account]["opening_balance"] = \
				accounts_by_name[d.parent_account].get("opening_balance", 0.0) + d.get("opening_balance", 0.0)

def accumulate_values_into_parents_es(accounts, accounts_by_name, period_list, accumulated_values):
	"""accumulate children's values in parent accounts"""
	for d in reversed(accounts):
		# frappe.msgprint(str(d.name))
		if d.name and d.is_group != 1:
			for period in period_list:
				accounts_by_name[d.name][period.key] = \
					(accounts_by_name[d.name].get(period.key, 0.0) + d.get(period.key, 0.0))/2
				

			accounts_by_name[d.name]["opening_balance"] = \
				accounts_by_name[d.name].get("opening_balance", 0.0) + d.get("opening_balance", 0.0)
			# frappe.msgprint(str(accounts_by_name[d.name]["opening_balance"]))

def prepare_data(fiscal_year, cost_center, accounts, balance_must_be, period_list, company_currency):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")
	
	for d in accounts:
		# add to output
		has_value = False
		total = 0
		row = frappe._dict({
			"account_name": d.account_name,
			"account": d.name,
			"parent_account": d.parent_account,
			"indent": flt(d.indent),
			"year_start_date": year_start_date,
			"year_end_date": year_end_date,
			"currency": company_currency,
			"opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be=="Debit" else -1)
		})
		for period in period_list:
			if d.get(period.key) and balance_must_be=="Credit":
				# change sign based on Debit or Credit, since calculation is done using (debit - credit)
				d[period.key] *= -1
		
			row[period.key] = flt(d.get(period.key, 0.0), 3)

			if abs(row[period.key]) >= 0.005:
				# ignore zero values
				has_value = True
				total += flt(row[period.key])

		row["has_value"] = has_value
		row["total"] = total
		data.append(row)
		
	return data
#Below code copied from above for the requirement of Expenditure Statement // Kinley Dorji Cheten Tshering 2021/03/21
def prepare_data_es(periodicity, fiscal_year, cost_center, business_activity, accounts, balance_must_be, period_list, company_currency):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")
	conditions = ""
	if cost_center:
		conditions += " and gle.cost_center = '{0}'".format(cost_center)
	if business_activity:
		conditions += " and gle.business_activity = '{0}'".format(business_activity)
	for d in accounts:
		# add to output
		year_start_date, year_end_date = frappe.db.get_value("Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"])
		actual_amount = 0
		budget = []
		progressive = []
		progressive_amount = 0
		# frappe.msgprint("reseting actual_amount = "+str(actual_amount))
		if not year_start_date and year_end_date:
			frappe.throw("Budget year is necessary!")
		else:
			# frappe.msgprint(str(d.name))
			### For budget calculation ------------------------------------------------------------------
			if not cost_center:
				if business_activity:
					if d.is_group == 1 and d.name not in ("Assets - DS", "Payments - DS"):
						budget = frappe.db.sql(""" select sum(ba.budget_amount) as budget_amount from `tabBudget Account` ba, `tabBudget` b where b.name = ba.parent and b.fiscal_year = '{0}' and ba.account in (select name from `tabAccount` a where a.parent_account = '{1}') and b.business_activity = '{2}' and ba.docstatus = 1""".format(fiscal_year, d.name, business_activity), as_dict = True)
					elif d.is_group != 1:
						budget = frappe.db.sql(""" select sum(ba.budget_amount) as budget_amount from `tabBudget Account` ba, `tabBudget` b where b.name = ba.parent and b.fiscal_year = '{0}' and ba.account = "{1}" and b.business_activity = '{2}' and ba.docstatus = 1""".format(fiscal_year, d.name, business_activity), as_dict = True)
				else:
					if d.is_group == 1 and d.name not in ("Assets - DS", "Payments - DS"):
						budget = frappe.db.sql(""" select sum(ba.budget_amount) as budget_amount from `tabBudget Account` ba, `tabBudget` b where b.name = ba.parent and b.fiscal_year = '{0}' and ba.account in (select name from `tabAccount` a where a.parent_account = '{1}') and ba.docstatus = 1""".format(fiscal_year, d.name), as_dict = True)
					elif d.is_group !=1:
						budget = frappe.db.sql("""select sum(ba.budget_amount) as budget_amount from `tabBudget Account` ba, `tabBudget` b where b.name = ba.parent and b.fiscal_year = '{0}' and ba.account = "{1}" and ba.docstatus = 1""".format(fiscal_year, d.name), as_dict = True)
			else:
				if business_activity:
					if d.is_group == 1 and d.name not in ("Assets - DS", "Payments - DS"):
						budget = frappe.db.sql(""" select sum(ba.budget_amount) as budget_amount from `tabBudget Account` ba, `tabBudget` b where b.name = ba.parent and b.fiscal_year = '{0}' and ba.account in (select name from `tabAccount` a where a.parent_account = '{1}') and b.cost_center = '{2}' and b.business_activity = '{3}' and ba.docstatus = 1""".format(fiscal_year, d.name, cost_center, business_activity), as_dict = True)
					if business_activity:
						budget = frappe.db.sql("""select sum(ba.budget_amount) as budget_amount from `tabBudget Account` ba, `tabBudget` b where b.name = ba.parent and b.fiscal_year = '{0}' and ba.account = "{1}" and b.cost_center = '{2}' and b.business_activity = '{3}'and ba.docstatus = 1""".format(fiscal_year, d.name, cost_center, business_activity), as_dict = True)
					
				else:
					if d.is_group == 1 and d.name not in ("Assets - DS", "Payments - DS"):
						budget = frappe.db.sql("""select sum(ba.budget_amount) as budget_amount from `tabBudget Account` ba, `tabBudget` b where b.name = ba.parent and b.fiscal_year = '{0}' and ba.account in (select name from `tabAccount` a where a.parent_account = '{1}') and b.cost_center = '{2}' and ba.docstatus = 1""".format(fiscal_year, d.name, cost_center), as_dict = True)
					elif d.is_group !=1:
						budget = frappe.db.sql("""select sum(ba.budget_amount) as budget_amount from `tabBudget Account` ba, `tabBudget` b where b.name = ba.parent and b.fiscal_year = '{0}' and ba.account = "{1}" and b.cost_center = '{2}' and ba.docstatus = 1""".format(fiscal_year, d.name, cost_center), as_dict = True)
			if budget:
				actual_amount = flt(budget[0].budget_amount)
			# ---------------------------------------------------------------------------------------------------
		#for yearly, monthly, half yearly, and quarterly 
		if periodicity in ("Yearly", "Monthly", "Half-Yearly","Quarterly"):
			if d.is_group == 1 and d.name not in ("Assets - DS", "Payments - DS"):
				period_amount = frappe.db.sql("""select sum(gle.debit-gle.credit) as amount from `tabGL Entry` gle where gle.account in (select name from `tabAccount` a where a.parent_account = "{0}") and gle.posting_date between '{1}' and '{2}' {3}
				and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not in (select name from `tabStock Entry` b where gle.voucher_no = b.name and b.purpose in ('Material Transfer','Material Receipt') and b.docstatus = 1) else 1 = 1 end
                """.format(d.name, year_start_date, year_end_date, conditions), as_dict = True)
				progressive = frappe.db.sql("""
					select sum(gle.debit-gle.credit) as progressive from `tabGL Entry` gle where gle.account in (select name from `tabAccount` a where a.parent_account = "{0}")
					and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not in (select name from `tabStock Entry` b where gle.voucher_no = b.name and b.purpose in ('Material Transfer','Material Receipt') and b.docstatus = 1) else 1 = 1 end
					and gle.posting_date between '{1}' and '{2}' {3}
				""".format(d.name, year_start_date, year_end_date, conditions), as_dict = True)
			else:
				period_amount = frappe.db.sql("""select sum(gle.debit-gle.credit) as amount from `tabGL Entry` gle where gle.account = "{0}"
                and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not in (select name from `tabStock Entry` b where gle.voucher_no = b.name and b.purpose in ('Material Transfer','Material Receipt') and b.docstatus = 1) else 1 = 1 end
                and gle.posting_date between '{1}' and '{2}' {3}""".format(d.name, year_start_date, year_end_date, conditions), as_dict = True)
				progressive = frappe.db.sql("""
					select sum(debit - credit) as progressive from `tabGL Entry` where account = "{0}"
					and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not in (select name from `tabStock Entry` b where gle.voucher_no = b.name and b.purpose in ('Material Transfer','Material Receipt') and b.docstatus = 1) else 1 = 1 end
					and posting_date between '{1}' and '{2}' {3}
				""".format(d.name, year_start_date, year_end_date, conditions), as_dict = True)
		#for individual month
		else:
			if d.is_group == 1 and d.name not in ("Assets - DS", "Payments - DS"):
				period_amount = frappe.db.sql("""select sum(gle.debit-gle.credit) as amount from `tabGL Entry` gle where gle.account in (select name from `tabAccount` a where a.parent_account = '{0}')
                and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not in (select name from `tabStock Entry` b where gle.voucher_no = b.name and b.purpose in ('Material Transfer','Material Receipt') and b.docstatus = 1) else 1 = 1 end
            	and gle.posting_date between '{1}' and '{2}' {3}
                """.format(d.name, period_list[0].from_date, period_list[0].to_date, conditions), as_dict = True)
				# query = """select sum(gle.debit-gle.credit) as amount from `tabGL Entry` gle where gle.account in (select name from `tabAccount` a where a.parent_account = '{0}')
                # and case when gle.voucher_type = 'Stock Entry' then exists(select 1 from `tabStock Entry` a where gle.voucher_no = a.name and a.purpose not in ('Material Transfer','Material Receipt')) else 1 = 1 end
            	# and gle.posting_date between '{1}' and '{2}' {3}
                # """.format(d.name, period_list[0].from_date, period_list[0].to_date, conditions)
				# if d.name == 'Maint. of property- vehicle - DS':
				# 	frappe.msgprint(query)
				progressive = frappe.db.sql("""
					select sum(gle.debit-gle.credit) as progressive from `tabGL Entry` gle where gle.account in (select name from `tabAccount` a where a.parent_account = '{0}')
					and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not in (select name from `tabStock Entry` b where gle.voucher_no = b.name and b.purpose in ('Material Transfer','Material Receipt') and b.docstatus = 1) else 1 = 1 end
					and gle.posting_date between '{1}' and '{2}' {3}
				""".format(d.name, year_start_date, period_list[0].to_date, conditions), as_dict = True)
			else:
				period_amount = frappe.db.sql("""select sum(gle.debit-gle.credit) as amount from `tabGL Entry` gle where gle.account = "{0}"
               	and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not in (select name from `tabStock Entry` b where gle.voucher_no = b.name and b.purpose in ('Material Transfer','Material Receipt') and b.docstatus = 1) else 1 = 1 end
                and gle.posting_date between '{1}' and '{2}' {3}
                """.format(d.name, period_list[0].from_date, period_list[0].to_date, conditions), as_dict = True)
				# period_amount = frappe.db.sql("""select sum(gle.debit-gle.credit) as amount from `tabGL Entry` gle where gle.account = "{0}"
                # and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not like '%SEMT%' or gle.voucher_no not like '%SEMR%' else 1 = 1 end
                # and gle.posting_date between '{1}' and '{2}' {3}
                # """.format(d.name, period_list[0].from_date, period_list[0].to_date, conditions), as_dict = True)
				# query = """select sum(gle.debit-gle.credit) as amount from `tabGL Entry` gle where gle.account = '{0}'
                # and case when gle.voucher_type = 'Stock Entry' then exists(select 1 from `tabStock Entry` a where gle.voucher_no = a.name and a.purpose not in ('Material Transfer','Material Receipt')) else 1 = 1 end
            	# and gle.posting_date between '{1}' and '{2}' {3}
                # """.format(d.name, period_list[0].from_date, period_list[0].to_date, conditions)
				# if d.name == 'Maint. of property- vehicle - DS':
				# 	frappe.msgprint(str(period_amount))
				progressive = frappe.db.sql("""
					select sum(debit - credit) as progressive from `tabGL Entry` gle where account = "{0}"
					and case when gle.voucher_type = 'Stock Entry' then gle.voucher_no not in (select name from `tabStock Entry` b where gle.voucher_no = b.name and b.purpose in ('Material Transfer','Material Receipt') and b.docstatus = 1) else 1 = 1 end
					and posting_date between '{1}' and '{2}' {3}
				""".format(d.name, year_start_date, period_list[0].to_date, conditions), as_dict = True)

		if progressive:
			progressive_amount = progressive[0].progressive
		has_value = False
		total = 0
		if d.name not in ("Assets - DS", "Payments - DS"):
			row = frappe._dict({
				"p_account_name": d.account_name if d.is_group == 1 else None,
				"p_account": d.name if d.is_group == 1 else None,
				"account_name": d.account_name if d.is_group == 0 else None,
				"account_code": d.account_code,
				"account": d.name if d.is_group == 0 else None,
				"actual_total": actual_amount,
				"progressive_amount": progressive_amount if progressive_amount else 0,
				"is_group": d.is_group,
				"parent_account": d.parent_account,
				"indent": flt(d.indent),
				"year_start_date": year_start_date,
				"year_end_date": year_end_date,
				"currency": company_currency,
				"opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be=="Debit" else -1)
			})
			for period in period_list:
				if d.get(period.key) and balance_must_be=="Credit":
					# change sign based on Debit or Credit, since calculation is done using (debit - credit)
					d[period.key] *= -1
				if d.is_group == 0:
					# row[period.key] = flt(d.get(period.key, 0.0), 3)
					row[period.key] = flt(period_amount[0].amount)

				elif d.is_group == 1 and d.name not in ("Asset - DS","Payments - DS"):
					row[period.key] = flt(period_amount[0].amount)
				if abs(row[period.key]) >= 0.005:
				# ignore zero values
					has_value = True
					total += flt(row[period.key])

			row["has_value"] = has_value
			row["total"] = total
			data.append(row)
	return data

def filter_out_zero_value_rows(data, parent_children_map, show_zero_values=False):
	data_with_value = []
	budget_total = progressive_total = 0
	for d in data:
		if d.is_group != 1:
			if show_zero_values or d.get("has_value"):
				data_with_value.append(d)
				# budget_total += d.actual_total
				# progressive_total += d.progressive_amount if d.progressive_amount else 0
		else:
			# show group with zero balance, if there are balances against child
			children = [child.name for child in parent_children_map.get(d.get("account")) or []]
			if children:
				for row in data:
					if row.get("account") in children and row.get("has_value"):
						data_with_value.append(d)
						# budget_total += row.actual_total
						# progressive_total += row.progressive_amount if row.progressive_amount else 0
						break

	return data_with_value, budget_total, progressive_total
#below method copied from above for Expenditure Statement
def filter_out_zero_value_rows_es(period_list, business_activity, data, parent_children_map, show_zero_values=False):
	data_with_value = []
	parent_accounts = []
	budget_total = progressive_total = 0
	for d in data:
		if d.is_group == 1 and d.get("has_value") and d[period_list[0].key] != 0:
			parent_accounts.append(d.p_account)
	# frappe.msgprint(str(data))

	for d in data:
		if d.is_group != 1:
			# if d.parent_account not in parent_accounts:
			# 	frappe.msgprint(d.account)
			if (show_zero_values) and d.parent_account in tuple(parent_accounts):
				data_with_value.append(d)
				# if d[period_list[0].key] != 0:
				# progressive_total += row.progressive_amount if row.progressive_amount else 0
			elif show_zero_values == 0 and d[period_list[0].key] != 0 and d.parent_account in tuple(parent_accounts):
				data_with_value.append(d)
				# budget_total += row.actual_total

		else:
			# show group with zero balance, if there are balances against child
			for row in data:
				if row.get("has_value") and d[period_list[0].key] != 0:
					budget_total += d.actual_total
					progressive_total += d.progressive_amount if d.progressive_amount else 0
					data_with_value.append(d)
					break

	return data_with_value, budget_total, progressive_total

def add_total_row(out, root_type, balance_must_be, period_list, company_currency):
	total_row = {
		"account_name": "'" + _("Total {0} ({1})").format(root_type, balance_must_be) + "'",
		#"account": "'" + _("Total {0} ({1})").format(root_type, balance_must_be) + "'",
		"account": None,
		"currency": company_currency
	}

	for row in out:
		if not row.get("parent_account"):
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)
				row[period.key] = ""

			total_row.setdefault("total", 0.0)
			total_row["total"] += flt(row["total"])
			row["total"] = ""

	if total_row.has_key("total"):
		out.append(total_row)

		# blank row after Total
		out.append({})

def add_total_row_es(out, balance_must_be, period_list, company_currency):
	total_row = {
		"account_name": "'" + _("Total({0})").format( balance_must_be) + "'",
		#"account": "'" + _("Total {0} ({1})").format(root_type, balance_must_be) + "'",
		"account": None,
		"currency": company_currency
	}
	total = 0
	for row in out:
		if row.get("parent_account") and row.is_group != 1:
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total += row.get(period.key, 0.0)
				# row[period.key] = ""

			# total_row.setdefault("total", 0.0)
			# total_row["total"] += flt(row["total"])
			# row["total"] = ""

	# if total_row.has_key("total"):
	# 	out.append(total_row)

	# 	# blank row after Total
	# 	out.append({})
	# frappe.msgprint(str(total_row[period.key]))
	return total

def get_accounts(company, exclude, root_type):
	accounts = frappe.db.sql("""select is_group, name, account_code, parent_account, lft, rgt, root_type, report_type, account_name from `tabAccount`
		where company='{0}' and root_type='{1}' and name not in {2} order by name asc""".format(company, root_type, tuple(exclude)), as_dict=True)
	# frappe.msgprint(str(accounts))
	return accounts
def filter_accounts(accounts, depth=10):
	parent_children_map = {}
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.name] = d
		# frappe.msgprint(str(accounts_by_name[d.name]))
		parent_children_map.setdefault(d.parent_account or None, []).append(d)

	filtered_accounts = []

	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			if parent == None:
				sort_root_accounts(children)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map

def filter_accounts_es(accounts, depth=2):
	parent_children_map = {}
	accounts_by_name = {}
	for d in accounts:
		accounts_by_name[d.name] = d
		# frappe.msgprint(str(accounts_by_name[d.name]))
		parent_children_map.setdefault(d.parent_account or None, []).append(d)

	filtered_accounts = []

	def add_to_list(parent, level):
		if level < depth:
			children = parent_children_map.get(parent) or []
			if parent == None:
				sort_root_accounts(children)

			for child in children:
				child.indent = level
				filtered_accounts.append(child)
				add_to_list(child.name, level + 1)

	add_to_list(None, 0)

	return filtered_accounts, accounts_by_name, parent_children_map

def sort_root_accounts(roots):
	"""Sort root types as Asset, Liability, Equity, Income, Expense"""

	def compare_roots(a, b):
		if a.report_type != b.report_type and a.report_type == "Balance Sheet":
			return -1
		if a.root_type != b.root_type and a.root_type == "Asset":
			return -1
		if a.root_type == "Liability" and b.root_type == "Equity":
			return -1
		if a.root_type == "Income" and b.root_type == "Expense":
			return -1
		return 1

	roots.sort(compare_roots)

#added parameter business_activity

def set_gl_entries_by_account(cost_center, business_activity, company, from_date, to_date, root_lft, root_rgt, gl_entries_by_account,
		ignore_closing_entries=False, open_date=None):
	"""Returns a dict like { "account": [gl entries], ... }"""
	additional_conditions = []

	if ignore_closing_entries:
		additional_conditions.append(" and ifnull(voucher_type, '')!='Period Closing Voucher' ")

	#if from_date:
	#	additional_conditions.append("and posting_date >= %(from_date)s")
	
	'''if business_activity:
		ba = " business_activity =   {0}".format(business_activity)
	else:
		ba = " 1 = 1 "
		
	frappe.msgprint("ba : {0}".format(ba))'''
	if business_activity:
                additional_conditions.append(" and business_activity = '{0}'".format(business_activity))
        else:
                additional_conditions.append(" and 1 = 1 ")

	if from_date and to_date:
		if open_date:
			#Getting openning balance
			additional_conditions.append(" and posting_date < \'" + str(open_date) + "\' and docstatus = 1 ")
		else:
			additional_conditions.append(" and posting_date BETWEEN %(from_date)s AND %(to_date)s and docstatus = 1 ")

	if not cost_center:
		gl_entries = frappe.db.sql("""select posting_date, account, debit, credit, is_opening from `tabGL Entry`
			where company=%(company)s
			{additional_conditions}
			and account in (select name from `tabAccount`
				where lft >= %(lft)s and rgt <= %(rgt)s)
			order by account, posting_date""".format(additional_conditions="\n".join(additional_conditions)),
			{
				"company": company,
				"from_date": from_date,
				"to_date": to_date,
				"lft": root_lft,
				"rgt": root_rgt
			},
			as_dict=True)

	else:
		cost_centers = get_child_cost_centers(cost_center);
		additional_conditions.append("and cost_center IN %(cost_center)s")
		gl_entries = frappe.db.sql("""select posting_date, account, debit, credit, is_opening from `tabGL Entry`
			where company=%(company)s
			{additional_conditions}
			and account in (select name from `tabAccount`
				where lft >= %(lft)s and rgt <= %(rgt)s)
			order by account, posting_date""".format(additional_conditions="\n".join(additional_conditions)),
			{
				"cost_center": cost_centers,
				"company": company,
				"from_date": from_date,
				"to_date": to_date,
				"lft": root_lft,
				"rgt": root_rgt
			},
			as_dict=True)

	for entry in gl_entries:
		gl_entries_by_account.setdefault(entry.account, []).append(entry)

	return gl_entries_by_account

def get_columns(periodicity, period_list, accumulated_values=1, company=None):
	columns = [{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 300
		},
		{
			"fieldname": "account_code",
			"label": _("Account Code"),
			"fieldtype": "Data",
			"width": 100
		}
		]
	if company:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
	for period in period_list:
		# frappe.msgprint(str(period.key)+str(period.label))
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		})
	columns.append(
		{
			"fieldname": "actual_total",
			"label": _("Actual Budget Amount"),
			"fieldtype": "Currency",
			"width": 200
		})
	columns.append({
			"fieldname": "progressive_amount",
			"label": _("Annual Progressive Amount"),
			"fieldtype": "Currency",
			"width": 200
		})
	# if periodicity!="Yearly":
	# 	if not accumulated_values:
	# 		columns.append({
	# 			"fieldname": "total",
	# 			"label": _("Total"),
	# 			"fieldtype": "Currency",
	# 			"width": 150
	# 		})
	

	return columns

def get_columns_es(periodicity, period_list, accumulated_values=1, company=None):
	columns = [
		{
			"fieldname": "p_account",
			"label": ("Parent Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 150
		},
		{
			"fieldname": "account",
			"label": _("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"width": 300
		},
		{
			"fieldname": "account_code",
			"label": _("Account Code"),
			"fieldtype": "Data",
			"width": 100
		}
		]
	if company:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
	for period in period_list:
		# frappe.msgprint(str(period.key)+str(period.label))
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		})
	columns.append(
		{
			"fieldname": "actual_total",
			"label": _("Actual Budget Amount"),
			"fieldtype": "Currency",
			"width": 200
		})
	columns.append({
			"fieldname": "progressive_amount",
			"label": _("Annual Progressive Amount"),
			"fieldtype": "Currency",
			"width": 200
		})
	# if periodicity!="Yearly":
	# 	if not accumulated_values:
	# 		columns.append({
	# 			"fieldname": "total",
	# 			"label": _("Total"),
	# 			"fieldtype": "Currency",
	# 			"width": 150
	# 		})
	

	return columns
