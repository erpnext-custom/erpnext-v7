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
                ("Posting Date") + ":Date:80",
		("Branch") + ":Data:120",
                ("Voucher No.") + ":Data:120",
                ("Mode of Payment") + ":Data:120",
                ("Paid Amount") + ":Currency:120",
		("Created By") + ":Data:120"
        ]

def get_data(filters):

        query =  "select posting_date, branch, name, mode_of_payment, paid_amount, submitted_by from `tabPayment Entry` where docstatus = 1"
	
	if filters.get("branch"):
                query += " and branch = \'"+ str(filters.branch) + "\'"

        if filters.get("from_date") and filters.get("to_date"):
                query += " and posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) +"\'"
        return frappe.db.sql(query)
