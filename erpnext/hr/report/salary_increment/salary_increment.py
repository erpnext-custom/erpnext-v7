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
                ("Name ") + ":Link/Salary Increment:200",
		("Branch ") + ":Link/Equipment:200",
                ("Employee ID") + ":Link/Employee:100",
                ("Employee Name") + ":Data:150",
		("Year") + ":Data:80",
                ("Month")+ ":Data:50",
                ("Current Basic") + ":Currency:120",
                ("Increment") + ":Currency:80",
                ("New Basic") + ":Currency:120"
        ]
def get_data(filters):
	#docstatus = ""
        if filters.uinput == "Draft":
                docstatus = 0
        if filters.uinput == "Submitted":
                docstatus = 1
        if filters.uinput == "All":
                docstatus = "docstatus"
        query =  """select name, branch, employee, employee_name, fiscal_year, month, old_basic, 
                    increment, new_basic 
                    from `tabSalary Increment` 
                    where docstatus = {0}
                """.format(docstatus)
        if filters.get("branch"):
                query += " and branch = \'"+ str(filters.branch) + "\'"
	if filters.get("fiscal_year"):
		query += " and fiscal_year = \'"+ str(filters.fiscal_year) + "\'"
	if filters.get("month") and filters.get("month") == 'January':
		query += " and month = 1 "
	if filters.get("month") and filters.get("month") == 'July':
		query += " and month = 6 " 
        #frappe.msgprint(docstatus)
        query += " order by branch"
        return frappe.db.sql(query, debug =1)
      
