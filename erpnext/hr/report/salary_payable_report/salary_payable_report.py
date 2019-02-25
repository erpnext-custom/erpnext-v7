# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr
from frappe import msgprint, _

def execute(filters=None):
        data    = []
        columns = []
       	columns  = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	conditions, filters = get_conditions(filters)
	d1 = []
	total = 0.0
	query = """select ss.employee, ss.employee_name, e.passport_number, ss.bank_name, ss.bank_account_no, ss.net_pay, ss.branch 
			from `tabSalary Slip` ss, 
			`tabEmployee` e
                        where ss.employee = e.name and ss.docstatus = 1 {0} order by ss.employee, ss.month""".format(conditions)
	for d in frappe.db.sql(query, as_dict =1):
		total += d.net_pay
		row = [d.employee, d.employee_name, d.passport_number, d.bank_name, d.bank_account_no, d.net_pay, d.branch]
		d1.append(row)
	d1.append({"net_pay": total, "employee": frappe.bold("TOTAL")})
	
	'''
	if not d1:
		msgprint(_("No Data Found for month: ") + cstr(filters.get("month")) + 
			_(" and year: ") + cstr(filters.get("fiscal_year")), raise_exception=1)
	'''

	return d1

def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", 
			"Dec"].index(filters.get("month")) + 1
		filters["month"] = month
		conditions += " and ss.month ={0}".format(month)
	
	if filters.get("fiscal_year"): conditions += " and ss.fiscal_year = \'" + str(filters.fiscal_year) + "\'"
	if filters.get("company"): conditions += " and ss.company = \'" + str(filters.company) + "\'"
	if filters.get("bank"): conditions += " and ss.bank_name = \'" + str(filters.bank) + "\'"
	
	return conditions, filters

def get_columns():
	columns = [
		{
		"fieldname": "employee",
		"label": "Employee Id",
		"fieldtype": "Link",
		"options": "Employee",
		"width": 120
		},
		{
		"fieldname": "employee_name",
		"label": "Name",
		"fieldtype": "Data",
		"width": 120,
		},
		{
		"fieldname": "passport_number",
		"label": "CID No",
		"fieldtype": "Data",
		"width": 120
		},
		{
		"fieldname":"bank_name",
		"label": "Bank Name",
		"fieldtype": "Data",
		"width": 120
		},
		{
		"fieldname": "bank_account_no",
		"label": "A/C No.",
		"fieldtype": "Data",
		"width": 120
		},
		{
		"fieldname": "net_pay",
		"label": "Amount",
		"fieldtype": "Currency",
		"width": 120
		},
		{
		"fieldname": "branch",
		"label": "Branch",
		"fieldtype": "Data",
		"width": 120
		}
	]
	return columns

