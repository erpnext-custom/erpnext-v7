# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# from __future__ import unicode_literals
# import frappe

# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import (get_period_list, get_columns_es, get_data_es, get_data)
import datetime

def execute(filters=None):
	if filters.show_zero_values:
		show_zero = 1
	else:
		show_zero = 0
	period_list = get_period_list(filters.fiscal_year, filters.periodicity)

	total_income = total_expense = total = 0
	exclude = [str("Bank & Cash - DS"), str("Inventories - DS"), str("Stock Assets - DS"), str("Tax - DS"), str("Temporary Accounts - DS"), str("Trade Receivables - DS"), str("Other Expenses - DS"), str("Stock Expenses - DS"), str("Accumulated Depreciation - DS"), str("Receipts - DS"), str("Property Plant and Equipment - DS")]
	income, total_income, income_budget, income_progressive = get_data_es(filters.fiscal_year, filters.cost_center, filters.business_activity, filters.company, "Asset", "Debit", exclude, period_list,
		accumulated_values=filters.accumulated_values, ignore_closing_entries=True, show_zero_values=show_zero, periodicity = filters.periodicity)
	expense, total_expense, expense_budget, expense_progressive  = get_data_es(filters.fiscal_year, filters.cost_center, filters.business_activity, filters.company, "Expense", "Debit", exclude, period_list,
		accumulated_values=filters.accumulated_values, ignore_closing_entries=True, show_zero_values=show_zero, periodicity = filters.periodicity)
	total = flt(total_income) + flt(total_expense)
	total_budget = (flt(income_budget)+flt(expense_budget))
	# frappe.throw(str(total_budget))
	total_progressive = (flt(income_progressive)+flt(expense_progressive))
	# set_gl_entries_by_account(filters.cost_center, filters.business_activity, filters.company, year_start_date, month_end, min_lft, max_rgt, gl_entries_by_account,  ignore_closing_entries=not flt(filters.with_period_closing_entry))

	# net_profit_loss = get_net_profit_loss(income, expense, period_list, filters.company)

	data = []
	data.extend(income or [])
	data.extend(expense or [])
	data.extend([{"p_account":"Total", period_list[0].key:flt(total), "actual_total":flt(total_budget), "progressive_amount":flt(total_progressive)}])
	
	# if net_profit_loss:
	# 	data.append(net_profit_loss)
	columns = get_columns_es(filters.periodicity, period_list, filters.accumulated_values, filters.company)
	# frappe.msgprint("columns:{}".format(columns))
	# data.append({"actual_total":actual_amount})
	# chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

	return columns, data, None


def get_net_profit_loss(income, expense, period_list, company):
	if income and expense:
		total = 0
		net_profit_loss = {
			"account_name": "'" + _("Net Profit / Loss") + "'",
			"account": None,
			"warn_if_negative": True,
			"currency": frappe.db.get_value("Company", company, "default_currency")
		}

		has_value = False

		for period in period_list:
			net_profit_loss[period.key] = flt(income[-2][period.key] - expense[-2][period.key], 3)

			if net_profit_loss[period.key]:
				has_value=True

			total += flt(net_profit_loss[period.key])
			net_profit_loss["total"] = total

		if has_value:
			return net_profit_loss

def get_chart_data(filters, columns, income, expense, net_profit_loss):
	x_intervals = ['x'] + [d.get("label") for d in columns[2:-1]]

	income_data, expense_data, net_profit = [], [], []

	for p in columns[2:]:
		if income:
			income_data.append(income[-2].get(p.get("fieldname")))
		if expense:
			expense_data.append(expense[-2].get(p.get("fieldname")))
		if net_profit_loss:
			net_profit.append(net_profit_loss.get(p.get("fieldname")))

	columns = [x_intervals]
	if income_data:
		columns.append(["Income"] + income_data)
	if expense_data:
		columns.append(["Expense"] + expense_data)
	if net_profit:
		columns.append(["Net Profit/Loss"] + net_profit)

	chart = {
		"data": {
			'x': 'x',
			'columns': columns
		}
	}

	if not filters.accumulated_values:
		chart["chart_type"] = "bar"

	return chart

