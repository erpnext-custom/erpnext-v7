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
		#("Production ID") + ":Link/Production Entry:120",
		("Branch") + ":Data:100",
		("Cost Center") + ":Data:100",
		("Location") + ":Date:100",
		("Warehouse")+ ":Data:100",
		("Item Name") + ":Data:120",
		("Item Code") + ":Data:100",
		("Item Group")+ ":Data:100",
		("Item Sub Group") + ":Data:100",
                ("Species") + ":Data:120",
		("Class") + ":Data:100",
                ("UoM") + ":Date:70",
                ("Quantity")+ ":Data:70",
                ("Rate") + ":Data:100",
                ("Posting Date") + ":Date:70",
                ("Business Activity")+ ":Data:90",
		("Company") + ":Data:90",

	]

def get_data(filters):
	query =  "Select pe.branch, pe.cost_center, pe.location, pe.warehouse, pe.item_name, pe.item_code, i.item_group, i.item_sub_group, i.species,(select ts.class from `tabTimber Species`as ts where ts.name = i.species) as class, pe.uom,sum(pe.qty) as quantity, pe.cop, pe.posting_date, pe.business_activity, pe.company from `tabProduction Entry` as  pe, tabItem i where pe.docstatus =1 and pe.item_code = i.item_code"
	if filters.get("branch"):
		query += " and pe.branch = \'"+ str(filters.branch) + "\'"
	if filters.get("from_date") and filters.get("to_date"):
		query += " and pe.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	
	query += " group by pe.item_code " 
	return frappe.db.sql(query)
