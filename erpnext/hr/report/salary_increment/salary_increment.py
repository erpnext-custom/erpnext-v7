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
                ("Branch ") + ":Link/Equipment:250",
                ("Employee ID") + ":Data:100",
                ("Employee Name") + ":Data:150",
		("Year") + ":Data:80",
                ("Month")+ ":Data:50",
                ("Current Basic") + ":Currency:120",
                ("Increment") + ":Currency:80",
                ("New Basic") + ":Currency:120"
        ]

def get_data(filters):
	docstatus = 1
        query =  "select branch, employee, employee_name, fiscal_year, month, old_basic, increment, new_basic from `tabSalary Increment` where docstatus = %s"
	if filters.uinput == "Draft":
		docstatus = 0

        if filters.get("branch"):
		query += " and branch = \'"+ str(filters.branch) + "\'"

	query += " order by branch"
        return frappe.db.sql(query, docstatus)

