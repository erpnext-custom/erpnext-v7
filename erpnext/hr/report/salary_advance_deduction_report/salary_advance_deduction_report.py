# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
def execute(filters=None):	
	columns = get_colums(filters)
	data = get_data(filters)
	return columns, data

def get_colums(filters=None): 
	columns = [

		_("Employee") + ":Link/Employee:155", 
		_("Employee Name") + "::150", 
		_("Designation") + ":Link/Designation:150",
        _("Branch") + ":Link/Branch:180", 
		_("From Date") + ":Date:120",
		_("Deduction Compoenent") + ":Link/Salary Component:170", 
		_("Deduction Amount") + ":Currency:150",

		# {
		#   	"fieldname": "employee",
		#   	"label": "Employee",
		#   	"fieldtype": "Link",
		# 	"options":"Employee",
		#   	"width": 155
		# },
		# {
		#   	"fieldname": "employee_name",
		#   	"label": "Employee Name",
		#   	"fieldtype": "Data",
		#   	"width": 150
		# },
		# {
		#   	"fieldname": "designation",
		#   	"label": "Designation",
		#   	"fieldtype": "Link",
		# 	"options":"Designation",
		#   	"width": 150
		# },
		# {
		#   	"fieldname": "branch",
		#   	"label": "Branch",
		#   	"fieldtype": "Link",
		# 	"options":"Branch",
		#   	"width": 180
		# },
		# {
		#   	"fieldname": "date",
		#   	"label": "From Date",
		#   	"fieldtype": "Date",
		#   	"width": 120
		# },
		# {
		#   	"fieldname": "deuction_component",
		#   	"label": "Deduction Component",
		#   	"fieldtype": "Data",
		#   	"width": 170
		# },
		# {
		#   	"fieldname": "deuction_amount",
		#   	"label": "Amount",
		#   	"fieldtype": "Currency",
		#   	"width": 150
		# },
	]
	return columns


def get_data(filters = None): 
	conditions = get_conditions(filters)
	data = """
		SELECT 
			ss.employee, ss.employee_name, ss.designation, ss.branch, ss.from_date, sd.salary_component, sd.amount
		FROM 
			`tabSalary Structure` as ss 
		JOIN
			`tabSalary Detail` as sd
		ON
			sd.parent = ss.name

		WHERE
			sd.salary_component IN ('House Rent', 'Salary Advance Deductions', 'Staff Welfare Loan') {cond}
		""".format(
			cond = conditions
		)
	
	return frappe.db.sql(data)	

def get_conditions(filters):
	conditions = ""

	if filters.get("branch"): 
		conditions += "and ss.branch = '{}' ".format(filters.get('branch'))
	if filters.get("employee"): 
		conditions += "and ss.employee = '{}' ".format(filters.get('employee'))
	if filters.get("from_date"): 
		conditions += "and ss.from_date >= '{}' ".format(filters.get('from_date'))

	return conditions


