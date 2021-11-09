# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.report.financial_statements import (get_period_list, get_columns, get_data)
from erpnext.accounts.report.profit_and_loss_statement.profit_and_loss_statement import get_net_profit_loss


def execute(filters=None):
	period_list = get_period_list(filters.fiscal_year, filters.periodicity)

	operation_accounts = {
		"section_name": "Operations",
		"section_footer": _("Cost Per MT Finished Products"),
		"section_header": _("Cost Per MT Finished Products"),
		"account_types": [
			{"acc_name": "mining_expenses", "label": _("Mining Cost per MT")},
			{"acc_name": "crushing_plant_expenses1", "label": _("Cost per MT Crushing Plant 1")},
			{"acc_name": "crushing_plant_expenses2", "label": _("Cost per MT Crushing Plant 2")},
			{"acc_name": "washed_expenses", "label": _("Cost Per MT Washed")}
		]
	}

	investing_accounts = {
		"section_name": "Investing",
		"section_footer": _("Cost per MT Finished Products at Stock Yard"),
		"section_header": _("Transportaion to Stockyard Cost per MT "),
		"account_types": [
			{"acc_name": "transportation", "label": _("Cost per MT Finished Products at Stock Yard")}
		]
	}

	financing_accounts = {
		"section_name": "Financing",
		"section_footer": _("Selling & Distribution Cost per MT"),
		"section_header": _("Cost per MT of Product sold"),
		"account_types": [
			{"acc_name": "s_and_d", "label": _("Cost per MT of Product sold")}
		]
	}

	# combine all cash flow accounts for iteration
	cash_flow_accounts = []
	cash_flow_accounts.append(operation_accounts)
	cash_flow_accounts.append(investing_accounts)
	cash_flow_accounts.append(financing_accounts)

	data = []
	company_currency = frappe.db.get_value("Company", filters.company, "default_currency")
	
	for cash_flow_account in cash_flow_accounts:

		section_data = []
		data.append({
			"account_name": cash_flow_account['section_header'], 
			"parent_account": None,
			"indent": 0.0, 
			"account": cash_flow_account['section_header']
		})

		for account in cash_flow_account['acc_name']:
			account_data = get_account_type_based_data(filters.company, 
				account['account_type'], period_list, filters.accumulated_values)
			account_data.update({
				"account_name": account['label'], 
				"indent": 1,
				"parent_account": cash_flow_account['section_header'],
				"currency": company_currency
			})
			data.append(account_data)
			section_data.append(account_data)

		add_total_row_account(data, section_data, cash_flow_account['section_header'], 
			period_list, company_currency)

	add_total_row_account(data, data, _("Net Change in Cash"), period_list, company_currency)
	columns = get_columns(filters)

	return columns, data


def get_columns():
        return [
                {
                        "fieldname": "particular",
                        "label": _("Particular"),
                        "fieldtype": "Link",
                        "width": 250
                },
                {
                        "fieldname": "total",
                        "label": _("Total"),
                        "fieldtype": "Currency",
                        "width": 120
                }
	]

def get_account_type_based_data(company, account_type, period_list, accumulated_values):
	data = {}
	total = 0
	for period in period_list:
		gl_sum = frappe.db.sql_list("""
			select sum(credit) - sum(debit)
			from `tabGL Entry`
			where company=%s and posting_date >= %s and posting_date <= %s 
				and voucher_type != 'Period Closing Voucher'
				and account in ( SELECT name FROM tabAccount WHERE account_type = %s)
		""", (company, period["year_start_date"] if accumulated_values else period['from_date'], 
			period['to_date'], account_type))
		
		if gl_sum and gl_sum[0]:
			amount = gl_sum[0]
			if account_type == "Depreciation":
				amount *= -1
		else:
			amount = 0
			
		total += amount
		data.setdefault(period["key"], amount)
		
	data["total"] = total
	return data


def add_total_row_account(out, data, label, period_list, currency):
	total_row = {
		"account_name": "'" + _("{0}").format(label) + "'",
		"account": None,
		"currency": currency
	}
	for row in data:
		if row.get("parent_account"):
			for period in period_list:
				total_row.setdefault(period.key, 0.0)
				total_row[period.key] += row.get(period.key, 0.0)
			
			total_row.setdefault("total", 0.0)
			total_row["total"] += row["total"]

	out.append(total_row)
	out.append({})
