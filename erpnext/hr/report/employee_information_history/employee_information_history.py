# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	query = """ select e.name as employee_id, e.employee_name,
	(select efd.cid_no from `tabEmployee Family Details` efd where efd.parent = e.name and efd.relationship = 'Self') as cid_no,
	e.date_of_birth, e.date_of_joining, e.gender,
	e.branch, e.department, e.division,
	(select ee.qualification from `tabEmployee Education` ee where ee.parent = e.name order by creation desc limit 1) as course,
	(select ee.level from `tabEmployee Education` ee where ee.parent = e.name order by creation desc limit 1) as qualification,
	(select ee.school_univ from `tabEmployee Education` ee where ee.parent = e.name order by creation desc limit 1) as school_univ,
	(select ee.country from `tabEmployee Education` ee where ee.parent = e.name order by creation desc limit 1) as country,
	e.cost_center, e.designation, e.status, e.relieving_date, e.reason_for_resignation,
	e.employment_status, e.company, e.employee_group, e.employment_type, e.employee_subgroup,
	ifnull((select sd.amount from `tabSalary Detail` sd, `tabSalary Structure` ss where ss.name = sd.parent and ss.employee = e.name and sd.salary_component = 'Basic Pay' and ss.is_active = "Yes"),0) as current_basic,
	e.approver_name, e.company_email from tabEmployee e where e.company = '{0}' """.format(filters.company)

	if filters.division:
		query +="and e.division = \'"+filters.division+"\'"
	
	if filters.cost_center:
		query += "and e.cost_center = \'"+filters.cost_center+"\'"
	# if filters.branch:
	# 	query+=" and branch = \'"+filters.branch+"\'"

	# if filters.warehouse:
	# 	query+=" and warehouse = \'"+filters.warehouse+"\'"

	# if filters.type:
	# 	query+=" and item_sub_group = \'"+filters.type+"\'"

	# if filters.item_code:
	# 	query+=" and item = \'"+filters.item_code+"\'"

	data = frappe.db.sql(query, as_dict=True)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "employee_id",
			"label": ("ID"),
			"fieldtype": "Link",
			"options" : "Employee",
			"width": 120
		},
		{
			"fieldname": "employee_name",
			"label": ("Employee Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "cid_no",
			"label": ("CID"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "date_of_birth",
			"label": ("DOB"),
			"fieldtype": "Date",
			"width": 120
		},
		{
			"fieldname": "date_of_joining",
			"label": ("Date of Appointment"),
			"fieldtype": "Date",
			"width": 130
		},
		{
			"fieldname": "gender",
			"label": ("Gender"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": 130
		},
		{
			"fieldname": "department",
			"label": ("Department"),
			"fieldtype": "Link",
			"options": "Department",
			"width": 130
		},
		{
			"fieldname": "division",
			"label": ("Division"),
			"fieldtype": "Link",
			"options": "Division",
			"width": 130
		},
		{
			"fieldname": "qualification",
			"label": ("Highest Qualification"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "course",
			"label": ("Course Name"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "school_univ",
			"label": ("School or University"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "country",
			"label": ("Course Country"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "designation",
			"label": ("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
			"width": 130
		},
		{
			"fieldname": "cost_center",
			"label": ("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 130
		},
		{
			"fieldname": "status",
			"label": ("Status"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "relieving_date",
			"label": ("Separation Date"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "reason_for_resignation",
			"label": ("Reason For Separation"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "employment_status",
			"label": ("Employment Status"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "company",
			"label": ("Company"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "employee_group",
			"label": ("Employee Group"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "employment_type",
			"label": ("Employment Type"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "employee_subgroup",
			"label": ("Employee Grade"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "current_basic",
			"label": ("Current Basic"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "approver_name",
			"label": ("Leave & Claim Approver"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "company_email",
			"label": ("Company Email"),
			"fieldtype": "Data",
			"width": 130
		},
		# {
		# 	"fieldname": "lot_no",
		# 	"label": _("Lot Number"),
		# 	"fieldtype": "Data",
		# 	"width": 120
		# },
		# {
		# 	"fieldname": "status",
		# 	"label": _("Status"),
		# 	"fieldtype": "Data",
		# 	"width": 120
		# },
		# {
		# 	"fieldname": "month",
		# 	"label": _("Month"),
		# 	"fieldtype": "Data",
		# 	"width": 130
		# },
		# {
		# 	"fieldname": "warehouse",
		# 	"label": _("Warehouse"),
		# 	"fieldtype": "Data",
		# 	"width": 130
		# },
	]
	
	return columns
