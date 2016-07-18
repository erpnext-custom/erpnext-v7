# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.accounts.report.financial_statements_emines \
	import filter_accounts, set_gl_entries_by_account, filter_out_zero_value_rows
from erpnext.accounts.utils import get_balance_on

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


def get_data(filters):
    data = [
	['Balance as at ' + str(frappe.utils.get_datetime(filters.from_date).strftime('%d %B, %Y')),"","","","","","","","","",""],
	['Profit/Loss after Income tax',"","","","","",str(get_balance_on("Retain Earnings - SMCL")),"","","",""],
	['Share allotment aganist money recieved from DHI',str(get_balance_on("Paid Up Capital - SMCL")/100)[1:],"100",str(get_balance_on("Paid Up Capital - SMCL"))[1:],"","","","","","",""],
    ['Dividend for the Financial Year',"","","","","",str(get_balance_on("Proposed Dividend (Current Year) - SMCL")),"","","",""],
	['Transfer to Group Investment Reserve',"","","","","","",str(get_balance_on("General Reserves - SMCL")),"","",""],
    ['Other Comprehensive Income for the Year',"","","","","","","","","",""],
	['Balance as at ' + str(frappe.utils.get_datetime(filters.to_date).strftime('%d %B, %Y')),"","","","","","","","","",""]
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
			"fieldname": "no_of_shares",
			"label": _("No. of Shares (issued and fully paid up)"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 150
		},
		{
			"fieldname": "per_share_value",
			"label": _("Par Value per Share"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 150
		},
		{
			"fieldname": "total_value_share",
			"label": _("Total Value of Shares"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 150
		},
		{
			"fieldname": "security_premium",
			"label": _("Security Premium"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 150
		},
		{
			"fieldname": "securities_other_reserves",
			"label": _("Securities & Other Reserves"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "retained_earnings",
			"label": _("Retained Earnings"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "general_reserves",
			"label": _("General Reserves"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "total",
			"label": _("Total"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "non_controlling_interest",
			"label": _("Non Controlling Interest"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		},
		{
			"fieldname": "total_equity",
			"label": _("Total Equity"),
			"fieldtype": "Data",
			"options": "Text",
			"width": 160
		}
	]
