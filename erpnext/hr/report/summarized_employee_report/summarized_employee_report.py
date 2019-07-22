# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import date_diff, get_last_day, nowdate, flt, getdate
def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_data(filters):
	data = []
	query = """ select name, passport_number, employee_name, gender, branch, date_of_birth,  designation, 
			date_of_joining, employment_type from `tabEmployee` 
			where status = 'Active'"""
	if filters.branch:
		query += " and branch = '{0}'".format(filters.get("branch"))
	
	if filters.employment_type:
		query += " and employment_type = '{0}'".format(filters.get("employment_type"))

	if filters.designation:
		query += " and designation = '{0}'".format(filters.get("designation"))
	
	for d in frappe.db.sql(query, as_dict =1):
		age  = round(date_diff(nowdate(), getdate(d.date_of_birth))/365.00,0)
		qualification = frappe.db.sql("""select qualification from `tabEmployee Education` where parent = '{0}' order by year_of_passing desc limit 1""".format(d.name))
		basic_pay = get_basic_pay(d.name)	
		row = [d.name, d.passport_number, d.employee_name, d.branch, d.gender, d.designation, d.employment_type, age, qualification, d.date_of_joining,\
			basic_pay]
		data.append(row)
	return data


def get_basic_pay(employee):
	ss = frappe.db.sql(""" select sd.amount 
				from `tabSalary Structure` ss, `tabSalary Detail` sd  
				where sd.parent = ss.name and ss.employee = '{0}' 
				and ss.is_active = 'Yes' and sd.salary_component = 'Basic Pay'""".format(employee), as_dict = True)
	if ss:
                return flt(ss[0].amount)
        else:
                return 0.0

def get_columns ():
	return [
		("EMP ID.") + ":Link/Employee:80",
		("CID NO") + ":Data:120",
		("Employee Name")+":Data:150",
		("Branch")+":Link/Branch:150",
		("Gender") + ":Data:70",
		("Designation") + ":Data:150",
		("Employee Type") + ":Data:150",
                ("Age") + ":Data:90",
                ("Qualification")+":Data:120",
                ("Date of Joining") + ":Date:110",
		("Basic Pay") + ":Currency:90",
	]
