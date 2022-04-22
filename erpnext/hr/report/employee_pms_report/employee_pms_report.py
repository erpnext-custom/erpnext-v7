# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	employees = frappe.db.sql("""
		select name, employee_name, passport_number,
		date_of_birth, date_of_joining, gender,
		branch, department, division from `tabEmployee`
		where status = 'Active'
	""",as_dict=1)
	yd = int(filters.to_fiscal_year)-int(filters.from_fiscal_year)+1
	years = []
	year_start = filters.from_fiscal_year
	for a in range(yd):
		years.append(str(int(year_start)))
		year_start = int(year_start)+1
	if employees:
		for a in employees:
			row = []
			row.append(a.name)
			row.append(a.employee_name)
			row.append(a.passport_number)
			row.append(a.date_of_birth)
			row.append(a.date_of_joining)
			row.append(a.gender)
			row.append(a.branch)
			row.append(a.department)
			row.append(a.division)
			for year in years:
				pms = frappe.db.sql("""select pms_rating from `tabEmployee PMS Rating` where fiscal_year ==  and parent = '{}' order by fiscal_year asc""".format(year, a.name)):
				if pms:
					row.append(pms)
				else:
					row.append(0)
			data.append(row)
	return data

def get_columns(filters):
	columns = [
				_("Employee") + ":Link/Employee:150", 
				_("Employee Name") + ":Data:150", 
				_("CID") + ":Data:120",
				_("DOB") + ":Date:120", 
				_("Date of Appointment") + ":Date:120",
				_("Gender") + ":Data:80",
				_("Branch") + ":Link/Branch:120",
				_("Department") + ":Link/Department:120",
				_("Division") + ":Link/Division:120",
			]
	if filters.to_fiscal_year < filters.from_fiscal_year:
		frappe.throw("To Fiscal Year cannot be before From Fiscal Year")
	yd = int(filters.to_fiscal_year)-int(filters.from_fiscal_year)+1
	year_start = filters.from_fiscal_year
	for a in range(yd):
		columns.append(str(int(year_start)) + ":Data:120")
		year_start = int(year_start)+1
	
	return columns


