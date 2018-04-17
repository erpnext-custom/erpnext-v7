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
		("Doc ID") + ":Link/Consumable Register Entry:120",
		("Material Code") + ":Link/Item:120",
		("Material Name") + ":Data:120",
		("Issue Date") + ":Date:120",
		("Issued To")+ ":Data:100",
		("Employee Name") + ":Data:120",
		("Quantity") + ":Data:70",
		("Ref Document")+ ":Link/Stock Entry:150",
	]

def get_data(filters):
	query =  "select a.name, a.item_code, (select b.item_name from tabItem b where b.item_code = a.item_code) as item_name, a.date, a.issued_to, (select c.employee_name from tabEmployee c where c.name = a.issued_to) as employee_name, a.qty, a.ref_doc from `tabConsumable Register Entry` a  where a.branch = \'" + filters.branch + "\' "
	if filters.get("from_date") and filters.get("to_date"):
		query += " and a.date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	return frappe.db.sql(query)
