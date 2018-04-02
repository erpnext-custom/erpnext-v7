# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document
from frappe.utils import nowdate

class ProjectMusterRollTool(Document):
	pass


@frappe.whitelist()
def get_employees(project, current_project=None):
	attendance_not_marked = []
	attendance_marked = []
	employee_list = []

	if current_project:
		employee_list = frappe.get_list("Muster Roll Employee", fields=["name", "person_name", "project"], filters={
			"status": "Active", "project": current_project}, order_by="person_name")

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
def transfer(employee_list, project, date_of_transfer):
	if not date_of_transfer:
		frappe.throw("Date of Transfer is Mandatory")
	employee_list = json.loads(employee_list)
	for employee in employee_list:
		mr = frappe.get_doc("Muster Roll Employee", employee['name'])
		branch, cc = frappe.db.get_value("Project", project, ['branch', 'cost_center'])
		if branch and cc:
			mr.project = project
			mr.branch = branch
			mr.cost_center = cc
			mr.date_of_transfer = date_of_transfer
			try:
				mr.save()
			except Exception as e:
                                frappe.throw("For MR Employee: <b style='color: red;'>{0}({1})</b>".format(mr.person_name, mr.name))

	frappe.msgprint("Successfully transferred following MR to {0}".format(project))
        for e in employee_list:
                frappe.msgprint("{0} ({1})".format(e['person_name'], e['name']))


