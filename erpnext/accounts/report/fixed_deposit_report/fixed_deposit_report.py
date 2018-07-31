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
		("Branch") + ":Data:120",
		("Bank Name") + ":Data:120",
		("FD #") + ":Data:120",
		("Principal Amount") + ":Currency:100",
		("Interest Rate") + ":Data:80",
		("Interest Amount") + ":Currency:120",
		("Total Amount") + ":Currency:120",
		("From  Date") + ":Data:80",
		("To  Date") + ":Data:80",
		("Status") + ":Data:80",
		("Overdraft") + ":Data:60"
	]	

def get_data(filters):
	query = """ select branch, bank, fd_number, principal, rate, i_amount, total_amount, start_date, end_date, status, overdaft from `tabFixed Deposit` where docstatus=1 """
	
	if filters.get("branch"):
		query += " and branch = \'"+ str(filters.get("branch")) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and start_date between \'" + str(filters.get("from_date")) + "\' and \'" + str(filters.get("to_date")) +"\'"
                query += " and end_date between \'" + str(filters.get("from_date")) + "\' and \'" + str(filters.get("to_date")) +"\'"

	'''
	if filters.get("branch"):
		query += " where branch = \'"+ str(filters.get("branch")) + "\'"

		if filters.get("from_date") and filters.get("to_date"):
			query += " and start_date between \'" + str(filters.get("from_date")) + "\' and \'" + str(filters.get("to_date")) +"\'"
	
			query += " and end_date between \'" + str(filters.get("from_date")) + "\' and \'" + str(filters.get("to_date")) +"\'"
	else:
		if filters.get("from_date") and filters.get("to_date"):
			query += " where start_date between \'" + str(filters.get("from_date")) + "\' and \'" + str(filters.get("to_date")) +"\'"

                	query += " and end_date between \'" + str(filters.get("from_date")) + "\' and \'" + str(filters.get("to_date")) +"\'"
	'''
	#frappe.msgprint(query) 
	return frappe.db.sql(query)

