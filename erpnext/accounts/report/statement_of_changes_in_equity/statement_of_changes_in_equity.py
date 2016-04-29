# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.accounts.report.financial_statements_emines \
	import filter_accounts, set_gl_entries_by_account, filter_out_zero_value_rows

value_fields = ("opening_debit", "opening_credit", "debit", "credit", "closing_debit", "closing_credit")

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):

	if not filters.fiscal_year:
		frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

	fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
	if not fiscal_year:
		frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
	else:
		filters.year_start_date = getdate(fiscal_year.year_start_date)
		filters.year_end_date = getdate(fiscal_year.year_end_date)

		filters.from_date = filters.year_start_date

def get_data(filters):
    data = [
	['Balance as at 1 January 2015','34634','34634','34634','34634','34634'],
	['Profit/Loss after Income tax','34634','34634','34634','34634','34634'],
	['Share allotment aganist money recieved from DHI','34634','34634','34634','34634','34634'],
    ['Dividend for the Financial Year','34634','34634','34634','34634','34634'],
	['Transfer to Group Investment Reserve','34634','34634','34634','34634','34634'],
    ['Other Comprehensive Income for the Year','34634','34634','34634','34634','34634'],
	['Balance as at 31 December 2016','34634','34634','34634','34634','34634']
	];
    return data
#     	accounts = frappe.db.sql("""select name, parent_account, account_name, root_type, report_type, lft, rgt
# 		from `tabAccount` where company=%s order by lft""", filters.company, as_dict=True)
#
# 	if not accounts:
# 		return None
#
# 	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)
#
# 	min_lft, max_rgt = frappe.db.sql("""select min(lft), max(rgt) from `tabAccount`
# 		where company=%s""", (filters.company,))[0]
#
# 	gl_entries_by_account = {}
#
# 	set_gl_entries_by_account(filters.cost_center, filters.company, filters.from_date,
# 		filters.to_date, min_lft, max_rgt, gl_entries_by_account, ignore_closing_entries=not flt(filters.with_period_closing_entry))
#
# 	opening_balances = get_opening_balances(filters)
#
# 	total_row = calculate_values(accounts, gl_entries_by_account, opening_balances, filters)
# 	accumulate_values_into_parents(accounts, accounts_by_name)
#
# 	data = prepare_data(accounts, filters, total_row, parent_children_map)
# 	data = filter_out_zero_value_rows(data, parent_children_map,
# 		show_zero_values=filters.get("show_zero_values"))
# */

def get_columns():
	return [
		{
			"fieldname": "statement",
			"label": _(""),
			"fieldtype": "Data",
			"options": "Text",
			"width": 300
		},
		{
			"fieldname": "opening_debit",
			"label": _("Equity Share Capital"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "opening_credit",
			"label": _("Revaluation Surplus"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "debit",
			"label": _("Retained Earnings"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "credit",
			"label": _("General Reserves/GIR"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "closing_debit",
			"label": _("Total Equity"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		}
	]
