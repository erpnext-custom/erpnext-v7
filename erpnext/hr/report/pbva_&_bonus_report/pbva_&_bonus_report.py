# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from operator import itemgetter
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
	validate_filters(filters);
	columns = get_columns(filters);
	# queries = construct_query(filters);
	data = get_data(filters);

	return columns, data, filters

def get_data(filters=None):
	data = []
	# datas = frappe.db.sql(query, as_dict=True);
	# frappe.msgprint(str(datas))
	# for d in datas:
	# 	row = [d.month, "Salary", d.basic_pay, round(flt(d.gross_pay) - flt(d.basic_pay) - (flt(d.comm_all) / 2), 2), round(flt(d.gross_pay)-(flt(d.comm_all) / 2),2), round(flt(d.gross_pay)-(flt(d.comm_all) / 2),2), d.nppf,d.gis, flt(d.gross_pay) - flt(d.nppf) - flt(d.gis) - (flt(d.comm_all) / 2), d.tds, d.health, d.receipt_number, d.receipt_date]
	# 	data.append(row);

	#Leave Encashment 

		#Bonus

	if filters.type == "Bonus":
		bonus = frappe.db.sql("""
				select b.name, b.fiscal_year, b.posting_date
				from `tabBonus` b
				where b.docstatus = 1 and b.posting_date between %s and %s 
				""", (str(filters.fiscal_year) + "-01-01", str(filters.fiscal_year) + "-12-31"), as_dict=1)
		if filters.employee:
			for b in bonus:
				amt = frappe.db.sql("""
				     	select a.employee as employee, a.employee_name, b.employee_group, b.employee_subgroup, a.branch,a.basic_pay, a.amount, a.tax_amount, a.balance_amount  
						from `tabBonus Details` a, `tabEmployee` b
						where a.parent = %s and a.employee = %s and a.employee = b.name 
				     	 """, (b.name, filters.employee), as_dict=1)
				for a in amt:
					row = [a.employee, a.employee_name, a.employee_group, a.employee_subgroup, a.branch, str(b.posting_date)[5:7], "Bonus", a.basic_pay, a.amount, a.amount, a.amount, a.tax_amount, a.amount - a.tax_amount]	
					data.append(row)
		else:
			if not filters.cost_center and not filters.branch:
				for b in bonus:
					amt = frappe.db.sql("""
				     	select b.employee, a.employee_name, b.employee_group, b.employee_subgroup, a.branch, a.basic_pay, a.amount, a.tax_amount, a.balance_amount  
						from `tabBonus Details` a, `tabEmployee` b
						where a.parent = %s and a.employee = b.name
				     	 """, (b.name), as_dict=1)
					for a in amt:
						row = [a.employee, a.employee_name, a.employee_group, a.employee_subgroup, a.branch, str(b.posting_date)[5:7], "Bonus", a.basic_pay, a.amount, a.amount, a.amount, a.tax_amount, a.amount - a.tax_amount]	
						data.append(row)

			elif not filters.branch:
				all_ccs = get_child_cost_centers(filters.cost_center)
				for b in bonus:
					amt = frappe.db.sql("""
				     	select b.employee, a.employee_name, b.employee_group, b.employee_subgroup, a.branch, a.basic_pay, a.amount, a.tax_amount, a.balance_amount  
						from `tabBonus Details` a, `tabEmployee` b
						where a.parent = %s and a.employee = b.name and a.branch in (select name from `tabBranch` where cost_center in %s)
				     	 """, (b.name, tuple(all_ccs)), as_dict=1)
					for a in amt:
						row = [a.employee, a.employee_name, a.employee_group, a.employee_subgroup, a.branch, str(b.posting_date)[5:7], "Bonus", a.basic_pay, a.amount, a.amount, a.amount, a.tax_amount, a.amount - a.tax_amount]	
						data.append(row)
			else:
				branch = str(filters.branch)
				branch = branch.replace(' - NRDCL','')
				for b in bonus:
					amt = frappe.db.sql("""
				     	select b.employee, a.employee_name, b.employee_group, b.employee_subgroup, a.branch, a.basic_pay, a.amount, a.tax_amount, a.balance_amount  
						from `tabBonus Details` a, `tabEmployee` b
						where a.parent = %s and a.employee = b.name and a.branch = %s
				     	 """, (b.name, branch), as_dict=1)
					for a in amt:
						row = [a.employee, a.employee_name, a.employee_group, a.employee_subgroup, a.branch, str(b.posting_date)[5:7], "Bonus", a.basic_pay, a.amount, a.amount, a.amount, a.tax_amount, a.amount - a.tax_amount]	
						data.append(row)				

			

	#PVBA
	else:
		pbva = frappe.db.sql("""
					select b.name, b.fiscal_year, b.posting_date
					from tabPBVA b
					where b.docstatus = 1 and b.posting_date between %s and %s 
				      """, (str(filters.fiscal_year) + "-01-01", str(filters.fiscal_year) + "-12-31"), as_dict=1)
		if filters.employee:
			for b in pbva:
				amt = frappe.db.sql("""
				     	select a.employee, a.employee_name, b.employee_group, b.employee_subgroup, a.branch, a.basic_pay, a.amount, a.tax_amount, a.balance_amount  
						from `tabPBVA Details` a, `tabEmployee` b
						where a.parent = %s and a.employee = %s and a.employee = b.name 
				      """, (b.name, filters.employee), as_dict=1)
				for a in amt:
					row = [a.employee, a.employee_name, a.employee_group, a.employee_subgroup, a.branch, str(b.posting_date)[5:7], "PBVA", a.basic_pay, a.amount, a.amount, a.amount, a.tax_amount, a.amount - a.tax_amount]	
					data.append(row)
		else:
			if not filters.cost_center and not filters.branch:
				for b in pbva:
					amt = frappe.db.sql("""
				     	select a.employee, a.employee_name, b.employee_group, b.employee_subgroup, a.branch, a.basic_pay, a.amount, a.tax_amount, a.balance_amount  
						from `tabPBVA Details` a, `tabEmployee` b
						where a.parent = %s and a.employee = b.name
				     	 """, (b.name), as_dict=1)
					for a in amt:
						row = [str(a.employee), a.employee_name, a.employee_group, a.employee_subgroup, a.branch, str(b.posting_date)[5:7], "PBVA", a.basic_pay, a.amount, a.amount, a.amount, a.tax_amount, a.amount - a.tax_amount]	
						data.append(row)

			elif not filters.branch:
				all_ccs = get_child_cost_centers(filters.cost_center)
				for b in pbva:
					amt = frappe.db.sql("""
				     	select a.employee, a.employee_name, b.employee_group, b.employee_subgroup, a.branch, a.basic_pay, a.amount, a.tax_amount, a.balance_amount  
						from `tabPBVA Details` a, `tabEmployee` b
						where a.parent = %s and a.employee = b.name and a.branch in (select name from `tabBranch` where cost_center in %s)
				     	 """, (b.name, tuple(all_ccs)), as_dict=1)
					for a in amt:
						row = [str(a.employee), a.employee_name, a.employee_group, a.employee_subgroup, a.branch, str(b.posting_date)[5:7], "PBVA", a.basic_pay, a.amount, a.amount, a.amount, a.tax_amount, a.amount - a.tax_amount]	
						data.append(row)
			
			else:
				branch = str(filters.branch)
				branch = branch.replace(' - NRDCL','')
				for b in pbva:
					amt = frappe.db.sql("""
				     	select a.employee, a.employee_name, b.employee_group, b.employee_subgroup, a.branch, a.basic_pay, a.amount, a.tax_amount, a.balance_amount  
						from `tabPBVA Details` a, `tabEmployee` b
						where a.parent = %s and a.employee = b.name and a.branch = %s
				     	 """, (b.name, branch), as_dict=1)
					for a in amt:
						row = [str(a.employee), a.employee_name, a.employee_group, a.employee_subgroup, a.branch, str(b.posting_date)[5:7], "PBVA", a.basic_pay, a.amount, a.amount, a.amount, a.tax_amount, a.amount - a.tax_amount]	
						data.append(row)


	data = sorted(data, key=itemgetter(0))
	for a in data:
		a[5] = get_month(a[5])
	# frappe.msgprint(str(data))
	return data

# def construct_query(filters=None):
# 	'''query = """select a.month, a.gross_pay,
# 		(select b.amount from `tabSalary Detail` b where salary_component = 'Basic Pay' and b.parent = a.name) as basic_pay,
# 		(select b.amount from `tabSalary Detail` b where salary_component = 'Salary Tax' and b.parent = a.name) as tds ,
# 		(select b.amount from `tabSalary Detail` b where salary_component = 'PF' and b.parent = a.name) as nppf ,
# 		(select b.amount from `tabSalary Detail` b where salary_component = 'Group Insurance Scheme' and b.parent = a.name) as gis ,
# 		(select b.amount from `tabSalary Detail` b where salary_component = 'Communication Allowance' and b.parent = a.name) as comm_all ,
# 		(select b.amount from `tabSalary Detail` b where salary_component = 'Health Contribution' and b.parent = a.name) as health,
# 		r.receipt_number, r.receipt_date
# 		 from `tabSalary Slip` a, `tabRRCO Receipt Entries` r
# 		 where a.fiscal_year = r.fiscal_year and a.month = r.month and a.docstatus = 1 and r.purpose = 'Employee Salary' and a.fiscal_year = """ + str(filters.fiscal_year)

# 	'''

# 	query = """select a.month, a.gross_pay,
#         (select b.amount from `tabSalary Detail` b where salary_component = 'Basic Pay' and b.parent = a.name) as basic_pay,
#         (select b.amount from `tabSalary Detail` b where salary_component = 'Salary Tax' and b.parent = a.name) as tds ,
#         (select b.amount from `tabSalary Detail` b where salary_component = 'PF' and b.parent = a.name) as nppf ,
#         (select b.amount from `tabSalary Detail` b where salary_component = 'Group Insurance Scheme' and b.parent = a.name) as gis ,
#         (select b.amount from `tabSalary Detail` b where salary_component = 'Communication Allowance' and b.parent = a.name) as comm_all ,
#         (select b.amount from `tabSalary Detail` b where salary_component = 'Health Contribution' and b.parent = a.name) as health,
#         r.receipt_number, r.receipt_date
#          from `tabSalary Slip` a, `tabRRCO Receipt Entries` r
#          where a.fiscal_year = r.fiscal_year and a.month = r.month and a.docstatus = 1
# 	 and exists (select 1 from `tabCost Center` where a.cost_center in (select name from `tabCost Center` where parent_cost_center = r.cost_center)) 
#          and r.purpose = 'Employee Salary' and a.fiscal_year = """ + str(filters.fiscal_year)

# 	if filters.employee:
# 		query = query + " AND a.employee = \'" + str(filters.employee) + "\'";

# 	query+=";";
	
# 	return query;

def validate_filters(filters):

	if not filters.fiscal_year:
		frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

	start, end = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"])
	filters.year_start = start
	filters.year_end = end

def get_columns(filters):
	if filters.type == "PBVA":
		return [
			{
			"fieldname": "employee",
			"label": "Employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 110
			},
			{
			"fieldname": "employee_name",
			"label": "Employee Name",
			"fieldtype": "Data",
			"width": 120
			},
			{
			"fieldname": "employee_group",
			"label": "Designation",
			"fieldtype": "Link",
			"options": "Employee Group",
			"width": 100
			},
			{
			"fieldname": "employee_subgroup",
			"label": "Grade",
			"fieldtype": "Data",
			"width": 100
			},
			{
			"fieldname": "branch",
			"label": "Branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 120
			},		
			{
			"fieldname": "month",
			"label": "Month",
			"fieldtype": "Data",
			"width": 100
			},
			{
			"fieldname": "type",
			"label": "Income Type",
			"fieldtype": "Data",
			"width": 100
			},
			{
			"fieldname": "basic",
			"label": "Basic Salary",
			"fieldtype": "Currency",
			"width": 150
			},
			{
			"fieldname": "gross",
			"label": "Gross Salary",
			"fieldtype": "Currency",
			"width": 150
			},
			{
			"fieldname": "total",
			"label": "Total Income",
			"fieldtype": "Currency",
			"width": 120
			},
			# {
			#   "fieldname": "pf",
			#   "label": "NPPF",
			#   "fieldtype": "Currency",
			#   "width": 120
			# },
			# {
			#   "fieldname": "gis",
			#   "label": "GIS",
			#   "fieldtype": "Currency",
			#   "width": 120
			# },
			{
			"fieldname": "taxable",
			"label": "Taxable Income",
			"fieldtype": "Currency",
			"width": 120
			},
			{
			"fieldname": "tds",
			"label": "TDS / PIT",
			"fieldtype": "Currency",
			"width": 120
			},
			{
			"fieldname": "net",
			"label": "Net Income",
			"fieldtype": "Currency",
			"width": 120
			}
			# {
			#   "fieldname": "health",
			#   "label": "Health",
			#   "fieldtype": "Currency",
			#   "width": 120
			# }
		]
	else:
		return [
		{
		  "fieldname": "employee",
		  "label": "Employee",
		  "fieldtype": "Link",
		  "options": "Employee",
		  "width": 110
		},
		{
		  "fieldname": "employee_name",
		  "label": "Employee Name",
		  "fieldtype": "Data",
		  "width": 120
		},
		{
		  "fieldname": "employee_group",
		  "label": "Designation",
		  "fieldtype": "Link",
		  "options": "Employee Group",
		  "width": 100
		},
		{
		  "fieldname": "employee_subgroup",
		  "label": "Grade",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "branch",
		  "label": "Branch",
		  "fieldtype": "Link",
		  "options": "Branch",
		  "width": 120
		},		
		{
		  "fieldname": "month",
		  "label": "Month",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "type",
		  "label": "Income Type",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "basic",
		  "label": "Basic Salary",
		  "fieldtype": "Currency",
		  "width": 150
		},
		{
		  "fieldname": "gross",
		  "label": "Bonus Amount",
		  "fieldtype": "Currency",
		  "width": 150
		},
		{
		  "fieldname": "total",
		  "label": "Total Income",
		  "fieldtype": "Currency",
		  "width": 120
		},
		# {
		#   "fieldname": "pf",
		#   "label": "NPPF",
		#   "fieldtype": "Currency",
		#   "width": 120
		# },
		# {
		#   "fieldname": "gis",
		#   "label": "GIS",
		#   "fieldtype": "Currency",
		#   "width": 120
		# },
		{
		  "fieldname": "taxable",
		  "label": "Taxable Income",
		  "fieldtype": "Currency",
		  "width": 120
		},
		{
		  "fieldname": "tds",
		  "label": "TDS / PIT",
		  "fieldtype": "Currency",
		  "width": 120
		},
		{
		  "fieldname": "net",
		  "label": "Net Income",
		  "fieldtype": "Currency",
		  "width": 120
		}
		# {
		#   "fieldname": "health",
		#   "label": "Health",
		#   "fieldtype": "Currency",
		#   "width": 120
		# }
	]

def get_month(month):
	if month == "01":
		return "January"
	elif month == "02":
		return "February"
	elif month == "03":
		return "March"
	elif month == "04":
		return "April"
	elif month == "05":
		return "May"
	elif month == "06":
		return "June"
	elif month == "07":
		return "July"
	elif month == "08":
		return "August"
	elif month == "09":
		return "September"
	elif month == "10":
		return "October"
	elif month == "11":
		return "November"
	elif month == "12":
		return "December"
	else:
		return "None"
