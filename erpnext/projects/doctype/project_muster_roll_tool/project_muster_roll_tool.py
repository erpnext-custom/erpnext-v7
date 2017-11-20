# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document


class ProjectMusterRollTool(Document):
	pass


@frappe.whitelist()
def get_employees(project, current_project=None):
	attendance_not_marked = []
	attendance_marked = []
	employee_list = frappe.get_list("Muster Roll Employee", fields=["name", "person_name", "project"], filters={
		"status": "Active", "project": current_project}, order_by="person_name")
	marked_employee = {}

	for employee in employee_list:
		if employee['project'] != project:
			attendance_not_marked.append(employee)
		else:
			attendance_marked.append(employee)
	return {
		"marked": attendance_marked,
		"unmarked": attendance_not_marked
	}


@frappe.whitelist()
def transfer(employee_list, project):
	employee_list = json.loads(employee_list)
	for employee in employee_list:
		attendance = frappe.get_doc("Muster Roll Employee", employee['name'])
		branch, cc = frappe.db.get_value("Project", project, ['branch', 'cost_center'])
		if branch and cc:
			attendance.project = project
			attendance.branch = branch
			attendance.cost_center = cc
			attendance.save()
