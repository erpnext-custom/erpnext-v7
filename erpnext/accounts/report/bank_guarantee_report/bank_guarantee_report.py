# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)


	return columns, data

def get_columns():
	return[
		("Bank Guarantee #") + ":Data:120",
		("Bank Name") + ":Data:120",
		("Project") + ":Data:120",
		("Customer") + ":Data:120",
		("Amount") + ":Currency:120",
		("Start Date") + ":Data:120",
		("End Date") + ":Data:120",
		("Custodian") + ":Data:120",
		("Purpose") + ":Data:120",
		("Status") + ":Data:120"
		]	

def get_data(filters):
	query = " select bank_guarantee_number, bank_name, project, customer, amount, start_date, end_date, custodian_name, purpose, guarantee_status from `tabBank Guarantee`"

	if filters.get("from_date") and filters.get("to_date"):
		query += " where start_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) +"\'"
	
		query += " and end_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) +"\'"
		
	#frappe.msgprint(query) 
	return frappe.db.sql(query) 

