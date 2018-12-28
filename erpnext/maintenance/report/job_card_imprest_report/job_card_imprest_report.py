# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)


	return columns, data

def get_columns():
	return [
		("Job Card No.") + ":Link/Job Card:120",
		("Posting Date") + ":Date:120",
		("Material Code")+ ":Data:100",
		("Material name") + ":Data:120",
		("Amount") + ":Currency:120"
	]

def get_data(filters):
	query =  "select jc.name, jc.posting_date,jci.job, jci.job_name, jci.amount from `tabJob Card` as jc,`tabJob Card Item` as jci  where jci.parent = jc.name and jc.docstatus = 1 and jci.imprest= 1"
	if filters.get("cost_center"):
		query += " and jc.cost_center = \'" + str(filters.cost_center) + "\'"
	if filters.get("from_date") and filters.get("to_date"):
		query += " and jc.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	return frappe.db.sql(query)
