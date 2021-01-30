# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	row = tot = {}
	duration = mandays = manpower =  weightage = physical_progress = percent_completed = 0.0
	query = construct_query(filters)
	for a in frappe.db.sql(query, as_dict = True):
		row = {"name": a.name, "expected_start_date": a.expected_start_date, 
		"expected_end_date": a.expected_end_date, "total_duration": a.total_duration, "estimated_budget": a.estimated_budget,  "physical_progress_weightage": a.physical_progress_weightage, 
		"physical_progress":  a.physical_progress, "percent_completed": a.percent_completed, "status": a.status, 
		"project_engineer": a.project_engineer, "engineer_name": a.pe_name, "contact": a.contact}
		data.append(row)	
		duration += flt(a.total_duration)
                mandays += flt(a.mandays)
                manpower += flt(a.man_power_required)
                weightage += flt(a.physical_progress_weightage)
                physical_progress += flt(a.physical_progress)
                percent_completed += flt(a.percent_completed)
		row = {"name": "<b> Overall </b> ", "expected_start_date": a.expected_start_date, 
                "expected_end_date": a.expected_end_date, "total_duration": duration, "mandays": mandays, 
                "man_power_required":  manpower, "physical_progress_weightage": weightage, 
                "physical_progress":  physical_progress, "percent_completed": percent_completed, "project_engineer": ""}
	data.append(row)
	return data

def construct_query(filters):
	cond = " and is_group = 1"
	if filters.get("project"):
		if filters.get("show_all"):
			frappe.throw("Cannot use filters with Show All, Un-Check <b> Show All </b>  to use other filters")
		cond = " and parent_project = '{0}'".format(filters.get("project"))
	if filters.get("activity"):
		if filters.get("show_all"):
			frappe.throw("Cannot use filters with Show All, Un-Check <b> Show All </b> to use other filters")
		cond = " and project_name = '{0}'".format(filters.get("activity"))
	if filters.get("status"):
		cond = " and status = '{0}'".format(filters.get("status"))
	if filters.get("show_all"):
		cond = " and is_group != 1"
	
	query = """ select name, project_name, expected_start_date, expected_end_date, total_duration, estimated_budget, physical_progress_weightage, physical_progress, percent_completed, status, project_engineer, pe_name, contact from `tabProject` where docstatus <= 1 """
	'''if filters.get("company"):
		cond =  " and parent_cost_center = '{0}'".format(filters.company)

	if filters.get("cost_center"):
		cond = " and parent_cost_center = '{0}' and is_group != 1".format(filters.get("cost_center"))

	if filters.get("branch"):
		cond = " and project_name = '{0}'".format(filters.get("branch"))'''
	query += cond 
	return query


def get_columns(filters):
        return [
                { "fieldname": "name", "label": _("Activity Name"),  "fieldtype": "Link",  "options": "Project", "width": 200 },
		{ "fieldname": "expected_start_date", "label": _("Start Date"),  "fieldtype": "Date", "width": 80 },
		{ "fieldname": "expected_end_date", "label": _("End Date"),  "fieldtype": "Date", "width": 80 },
                { "fieldname": "total_duration", "label": _("Duration(Days)"),  "fieldtype": "Int", "width": 100 },
		{ "fieldname": "estimated_budget", "label": _("Estimated Budget"),  "fieldtype": "Currency", "width": 150 },
                { "fieldname": "expense_incured", "label": _("Expense Incurred"),  "fieldtype": "Currency", "width": 130 },
                { "fieldname": "physical_progress_weightage", "label": _("Weightage"),  "fieldtype": "Percent",  "width": 90 },
                { "fieldname": "physical_progress", "label": _("Achievement"),  "fieldtype": "Percent", "width": 100 },	
		{ "fieldname": "percent_completed", "label": _("Progress(%)"),  "fieldtype": "Percent", "width": 100 },
                { "fieldname": "status", "label": _("Status(%)"),  "fieldtype": "Data", "width": 100 },
		{ "fieldname": "project_engineer", "label": _("Project Engineer/Manager"),  "fieldtype": "Link",  "options": "Employee", "width": 140 },
		{ "fieldname": "engineer_name", "label": _("PE/PM Name"),  "fieldtype": "Data", "width": 140 },
		{ "fieldname": "contact", "label": _("Contact No."),  "fieldtype": "Data", "width": 140 }
	]
