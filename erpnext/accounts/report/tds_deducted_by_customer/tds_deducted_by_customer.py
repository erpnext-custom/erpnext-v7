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
		("Branch") + ":Link/Branch:120",
		("Date") + ":Date:120",
		("Invoice No.") + ":Data:120",
		("Customer") + ":Data:120",
		("Gross Amount")+ ":Data:120",
		("TDS Amount") + ":Data:120"

	]
	
def get_data(filters):

	query= (""" select pe.branch, pe.posting_date,per.reference_name, pe.party, pe.base_total_allocated_amount, pe.tds_amount from `tabPayment Entry` as pe, `tabPayment Entry Reference` as per where per.parent= pe.name and pe.tds_amount != 0 and pe.docstatus=1 """)

	if filters.get("from_date") and filters.get("to_date"):

		query += " and pe.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"

	return frappe.db.sql(query)	
