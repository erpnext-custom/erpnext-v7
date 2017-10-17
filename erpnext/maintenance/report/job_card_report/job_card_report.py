# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	conditions = get_conditions(filters)


	return columns, data

def get_columns():
	return [
		("Job Card No.") + ":Link/Job Card:120",
		("Posting Date") + ":Date:120",
		("Material Code")+ ":Data:100",
		("Material name") + ":Data:120",
		("Amount") + ":Data:120"
	]

def get_data(filters):
	conditions = get_conditions(filters)
	filters = get_conditions(filters)
	data =  frappe.db.sql("""select jc.name, jc.posting_date,jci.job, jci.job_name, jci.amount from `tabJob Card` as jc,`tabJob Card Item` as jci  where jci.parent = jc.name and jc.docstatus = 1 and jci.imprest= 1"""  (conditions,),filters)
	return data

def get_conditions(filters):
	conditions = ""
	if filters.get("cost_center"):
		conditions += " and jc.cost_center = %(cost_center)s"
		#query += " and jc.cost_center = \'" + str(filters.cost_center) + "\'"
			#query += "and jc.  = \'" + str(filters.cost_center) + "\'
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and jc.posting_date between %(from_date)s and %(to_date)s"
		#query += " and jc.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	return conditions
