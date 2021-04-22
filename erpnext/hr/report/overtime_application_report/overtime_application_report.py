# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns,data = get_columns(),get_data(filters)
	# frappe.msgprint(format())
	return columns, data

def get_data(filters):
    query = """
            SELECT oa.name,
				oa.employee,
				oa.employee_name,
				oa.branch,
				e.designation,
				oa.total_hours,
				oa.rate,
				oa.total_amount,
				e.bank_name,
				e.bank_ac_no,
				oa.purpose,
				oa.approver,
				oa.submission
			FROM `tabOvertime Application` oa
			INNER JOIN `tabEmployee` e ON oa.employee = e.name
			WHERE oa.docstatus = 1
			AND oa.branch = '{}'
			AND oa.submission BETWEEN '{}' AND '{}'
         """.format(filters.branch,filters.from_date,filters.to_date)
    if filters.employee :
        query += " AND oa.employee = '{}'".format(filters.employee)
    return frappe.db.sql(query)

def get_columns():
    return [
			("Reference") + ":Link/Overtime Application:100",
			("Employee ID") + ":Link/Employee:120",
			("Employee Name") + ":Data:120",
  			("Branch") + ":Link/Branch:200",
     		("Designation") + ":Link/Designation:100",
       		("Total Hours") + ":Float:100",
         	("Hourly Rate") + ":Float:100",
            ("Total Amount") + ":Float:100",
            ("Bank Name") + ":Link/Account:100",
            ("Account No") + ":Data:120",
            ("Purpose") + ":Data:200",
            ("Approver") + ":Data:200",
            ("Date") + ":Date:120"
	]
	