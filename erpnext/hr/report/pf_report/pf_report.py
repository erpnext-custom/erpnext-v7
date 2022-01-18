
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
        data    = []
        columns = []
        
	data = get_data(filters)
	if not data:
                return columns, data
        
	columns = get_columns(data)
	
	return columns, data
	
def get_columns(data):
	columns = [
		_("Parent Agency Name") + ":Data:90", 
		_("DeptCode") + ":Data:80", 
		_("Agency Name") + ":Link/Company:120", 
		_("NPPF Agency Code") + "::120",
		_("Month Name") + "::80",
		_("Financial Year") + "::80",
		_("Emp Name") + "::140", 
		_("CIDWPNo") + "::120", 
		_("PFACNo") + "::120",
		_("Grade") + "::80",
		_("Designation") + ":Link/Designation:120",
		_("Basic Pay") + ":Currency:120",
		_("Regular PFAmtEmployee") + ":Currency:120", 
		_("Regular PFAmtEmployer") + ":Currency:120", 
		_("Cost Center") + ":Link/Cost Center:120"
		# _("Employee") + ":Link/Employee:80",
		# _("NPPF Tier") + "::80", 
		# _("Total") + ":Currency:120",
		# _("Branch") + ":Link/Branch:120", 
		# _("Department") + ":Link/Department:120",
		# _("Division") + ":Link/Division:120",
		# _("Section") + ":Link/Section:120", 
	]
	
	return columns
	
def get_data(filters):
	conditions, filters = get_conditions(filters)
	data = frappe.db.sql("""
			select 
				'','',
				t1.company as agency_name,
				t3.nppf_agency_code,
				CASE
					WHEN t1.month = '01'
						THEN 'January'
					WHEN t1.month = '02'
						THEN 'February'
					WHEN t1.month = '03'
						THEN 'March'
					WHEN t1.month = '04'
						THEN 'April'
					WHEN t1.month = '05'
						THEN 'May'
					WHEN t1.month = '06'
						THEN 'June'
					WHEN t1.month = '07'
						THEN 'July'
					WHEN t1.month = '08'
						THEN 'August'
					WHEN t1.month = '09'
						THEN 'September'
					WHEN t1.month = '10'
						THEN 'October'
					WHEN t1.month = '11'
						THEN 'November'
					ELSE
						'December'
				END AS month,
				t1.fiscal_year,
				t3.employee_name,
				t3.passport_number,
				t3.nppf_number,
				t1.employee_grade,
				t1.designation, 
				sum(case when t2.salary_component = 'Basic Pay' then ifnull(t2.amount,0) else 0 end) as basicpay,
				sum(case when t2.salary_component = 'PF' then ifnull(t2.amount,0) else 0 end) as employeepf,
				(0.015*t2.amount) as employerpf,
				t1.cost_center
				from `tabSalary Slip` t1, `tabSalary Detail` t2, `tabEmployee` t3
				where t1.docstatus = 1 %s
				and t3.employee = t1.employee
				and t2.parent = t1.name
				and t2.salary_component in ('Basic Pay','PF')
				group by t1.employee, t3.employee_name, t1.designation, t3.passport_number,
			t3.nppf_number, t1.company, t1.branch, t1.department, t1.division, t1.section, t1.cost_center,
				t1.fiscal_year, t1.month
			""" % conditions, filters)	
 #t1.employer_pf as employerpf,
	return data
	
def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", 
			"Dec"].index(filters["month"]) + 1
		filters["month"] = month
		conditions += " and t1.month = %(month)s"
	
	if filters.get("fiscal_year"): conditions += " and t1.fiscal_year = %(fiscal_year)s"
	if filters.get("company"): conditions += " and t1.company = %(company)s"
	if filters.get("employee"): conditions += " and t1.employee = %(employee)s"
	# if filters.get("tier"): conditions += " and t3.nppf_tiers = %(tier)s"
	
	return conditions, filters
	

# from __future__ import unicode_literals
# import frappe
# from frappe.utils import flt, cstr
# from frappe import msgprint, _

# def execute(filters=None):
# 	if not filters: filters = {}
#         data    = []
#         columns = []
        
# 	data = get_data(filters)
# 	if not data:
#                 return columns, data
        
# 	columns = get_columns(data)
	
# 	return columns, data
	
# def get_columns(data):
# 	columns = [
# 		_("Employee") + ":Link/Employee:80", _("Employee Name") + "::140", _("Designation") + ":Link/Designation:120",
#                 _("CID") + "::120",_("NPPF Tier") + "::100", _("Basic Pay") + ":Currency:120",_("PF Account#") + "::120",
#                 _("Employee PF") + ":Currency:120", _("Employer PF") + ":Currency:120", _("Total") + ":Currency:120",
#                 _("Company") + ":Link/Branch:120", _("Branch") + ":Link/Branch:120", _("Department") + ":Link/Department:120",
#                 _("Division") + ":Link/Division:120", _("Section") + ":Link/Section:120", _("Year") + "::80", _("Month") + "::80"
# 	]
	
# 	return columns
	
# def get_data(filters):
# 	conditions, filters = get_conditions(filters)

#         data = frappe.db.sql("""
#                 select t1.employee, t3.employee_name, t1.designation, t3.passport_number,t3.nppf_tiers,
#                         sum(case when t2.salary_component = 'Basic Pay' then ifnull(t2.amount,0) else 0 end) as basicpay,
#                         t3.nppf_number,
#                         sum(case when t2.salary_component = 'PF' then ifnull(t2.amount,0) else 0 end) as employeepf,
#                         sum(case when t2.salary_component = 'PF' then ifnull(t2.amount,0) else 0 end) as employerpf,
#                         sum(case when t2.salary_component = 'PF' then ifnull(t2.amount,0)*2 else 0 end) as total,
#                         t1.company, t1.branch, t1.department, t1.division, t1.section,
#                         t1.fiscal_year, t1.month
#                 from `tabSalary Slip` t1, `tabSalary Detail` t2, `tabEmployee` t3
#                 where t1.docstatus = 1 %s
#                 and t3.employee = t1.employee
#                 and t2.parent = t1.name
#                 and t2.salary_component in ('Basic Pay','PF')
#                 group by t1.employee, t3.employee_name, t1.designation, t3.passport_number,
#                         t3.nppf_number, t1.company, t1.branch, t1.department, t1.division, t1.section,
#                         t1.fiscal_year, t1.month
#                 """ % conditions, filters)

# 	'''	
# 	if not data:
# 		msgprint(_("No Data Found for month: ") + cstr(filters.get("month")) + 
# 			_(" and year: ") + cstr(filters.get("fiscal_year")), raise_exception=1)
# 	'''
	
# 	return data
	
# def get_conditions(filters):
# 	conditions = ""
# 	if filters.get("month"):
# 		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", 
# 			"Dec"].index(filters["month"]) + 1
# 		filters["month"] = month
# 		conditions += " and t1.month = %(month)s"
	
# 	if filters.get("fiscal_year"): conditions += " and t1.fiscal_year = %(fiscal_year)s"
# 	if filters.get("company"): conditions += " and t1.company = %(company)s"
# 	if filters.get("employee"): conditions += " and t1.employee = %(employee)s"
# 	if filters.get("tier"): conditions += " and t3.nppf_tiers = %(tier)s"
	
# 	return conditions, filters
	
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt