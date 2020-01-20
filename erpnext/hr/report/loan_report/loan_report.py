# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SSK		                   03/08/2016         Taking care of Duplication of columns
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}

	data = get_data(filters)
	columns = get_columns(data)
	
	return columns, data
	
def get_columns(data):
	columns = [
		_("Employee") + ":Link/Employee:80", _("Employee Name") + "::140", _("Designation") + ":Link/Designation:120",
                _("CID") + "::120", _("Loan Type") + "::140", _("Bank Name") + "::160", _("Account No") + "::140", _("Amount") + ":Currency:140",
                _("Company") + ":Link/Branch:120", _("Branch") + ":Link/Branch:120", _("Department") + ":Link/Department:120",
                _("Division") + ":Link/Division:120", _("Section") + ":Link/Section:120", _("Year") + "::80", _("Month") + "::80"
	]
	
	return columns
	
def get_data(filters):
	conditions, filters = get_conditions(filters)
	status = "t1.docstatus <=2"
	if filters.get("process_status") == "All":
		status = "t1.docstatus <= 2"
        if filters.get("process_status") == "Submitted":
		status = "t1.docstatus = 1"
        if filters.get("process_status") == "Cancelled":
		status = "t1.docstatus = 2"
        if filters.get("process_status") == "Un-Submitted":
		status = "t1.docstatus = 0"
        
	query = """
                select t1.employee, t3.employee_name, t1.designation, t3.passport_number,
                        t2.reference_type, t2.institution_name, t2.reference_number, t2.amount,
                        t1.company, t1.branch, t1.department, t1.division, t1.section,
                        t1.fiscal_year, t1.month
                from `tabSalary Slip` t1, `tabSalary Detail` t2, `tabEmployee` t3
                where {0} {1}
                and t3.employee = t1.employee
                and t2.parent = t1.name
                and t2.parentfield = 'deductions'
                and exists(select 1
                                from `tabSalary Component` sc
                                where sc.name = t2.salary_component
                                and sc.gl_head = 'Financial Institution Loan - SMCL')
                """.format(status, conditions)
		
	data = frappe.db.sql(query)
	if not data:
		msgprint(_("No Data Found for month: ") + cstr(filters.get("month")) + 
			_(" and year: ") + cstr(filters.get("fiscal_year")), raise_exception=1)
	
	return data
	
def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", 
			"Dec"].index(filters["month"]) + 1
		filters["month"] = month
		conditions += " and t1.month = {0}".format(month)
	
	if filters.get("fiscal_year"): conditions += " and t1.fiscal_year = '{0}'".format(filters.get("fiscal_year"))
	if filters.get("company"): conditions += " and t1.company = '{0}'".format(filters.get("company"))
	if filters.get("employee"): conditions += " and t1.employee = '{0}'".format(filters.get("employee"))
	return conditions, filters
	
