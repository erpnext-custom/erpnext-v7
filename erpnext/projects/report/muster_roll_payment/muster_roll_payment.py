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
                ("Name ") + ":Data:100",
                ("CID") + ":Data:100",
                ("Branch") + ":Data:200",
                ("Unit") + ":Data:100",
                ("Wage Per Day") + ":Currency:100", 
				("Bank Name") + ":Data:100"
				("Bank Account") + ":Data:100"
        ]
# NEED TO GET DATA FOR NET PAY AND BANK ACCOUNT
def get_data(filters):
	query = """
		SELECT 
			person_name,
			name, 
			branch, 
			unit, 
			rate_per_day, 
			bank_name,
			bank_ac_no
		FROM 
			`tabMuster Roll Employee` 
		WHERE 
			status ='Active' 
	"""
	if filters.get("branch"):
		query += " and branch = \'" + str(filters.branch) + "\'"
	

	return frappe.db.sql(query)


