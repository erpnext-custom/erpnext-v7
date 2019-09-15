# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_data(filters):
	query = """ select posting_date, name, party_type, party, cost_center, payment_type, debit_account, amount, taxable_amount, tds_amount, net_amount from `tabDirect Payment` where docstatus = 1"""
	if filters.get("branch"):
		query += " and branch = '{0}'".format(filters.get("branch"))
	if filters.get("from_date") and filters.get("to_date"):
		query += " and posting_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
	
	return frappe.db.sql(query) 

def get_columns():
	return [
		("Posting Date") + ":Date:80",
		("Voucher Number") + ":Link/Direct Payment:120",
		("Party Type") + ":Data:80",
		("Party") + ":Data:140",
		("Cost Center") + ":Link/Cost Center: 190",
		("Payment Type") + ":Payment Type:90",
		("Debit Account") + ":Link/Account: 150",
		("Amount") + ":Currency:100",
		("Taxable Amount") + ":Currency:100",
                ("TDS Amount") + ":Currency:100",
                ("Net Amount") + ":Currency: 100"
	]
