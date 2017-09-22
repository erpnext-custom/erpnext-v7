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
		("Entry Type") + ":Data:150",
                ("Title") + ":Data:250",
                ("Posting Date") + ":Date:100",
                ("Voucher No.") + ":Link/Journal Entry:140"
       	]
 
def get_data(filters):
	query = """ select voucher_type, title, posting_date, name from `tabJournal Entry` where docstatus = 1 """

	if filters.get("branch"):
		query += "and branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += "and posting_date between \'" + str(filters.from_date) +"\' and \'" + str(filters.to_date) + "\'"
        
	return frappe.db.sql(query)
