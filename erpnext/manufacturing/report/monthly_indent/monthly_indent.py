# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)


	return columns, data

def get_columns():
	return [
		("Branch") + ":Data:100",
		("Item Code") + ":Link/Item:100",
		("Item Name") + ":Data:120",
		("Type") + ":Data:100",
		("Quantity")+ ":Data:80",
		("Rate") + ":Currency:100",
		("Amount") + ":Currency:110",
		("Delivery Date") + ":Date:100",
                ("Remarks")+ ":Data:150",
                ("Purpose") + ":Data:120",
		("Status")+ ":Data:120",
	]

def get_data(filters):
	query= """select m.branch, d.item_code, d.item_name, d.type, d.quantity, d.rate, d.amount, d.delivery_date, d.remarks, d.purpose, m.status from `tabMonthly Indent` m, `tabIndent Detail` d where d.parent= m.name and m.fiscal_year = '{0}' """.format(filters.get("year"))

	if filters.month:
		query += " and m.indent_for_month = \'"+ str(filters.month) +"\'"

	return frappe.db.sql(query) 
