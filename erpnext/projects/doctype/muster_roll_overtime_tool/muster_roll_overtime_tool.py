# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document


class MusterRollOvertimeTool(Document):
	pass


@frappe.whitelist()
def get_employees(project, date, number_of_hours):
	attendance_not_marked = []
	attendance_marked = []
	employee_list = frappe.get_list("Muster Roll Employee", fields=["name", "person_name"], filters={
		"status": "Active", "project": project}, order_by="person_name")
	marked_employee = {}
	for emp in frappe.get_list("Overtime Entry", fields=["number", "number_of_hours"],
							   filters={"date": date}):
		marked_employee[emp['number']] = emp['number']

	for employee in employee_list:
		if employee['name'] not in marked_employee:
			attendance_not_marked.append(employee)
		else:
			attendance_marked.append(employee)
	return {
		"marked": attendance_marked,
		"unmarked": attendance_not_marked
	}


@frappe.whitelist()
def allocate_overtime(employee_list, project, date, number_of_hours, purpose=None):
	employee_list = json.loads(employee_list)
	for employee in employee_list:
		attendance = frappe.new_doc("Overtime Entry")
		attendance.date = date
		attendance.project = project
		attendance.purpose = purpose
		attendance.number_of_hours = number_of_hours
		attendance.number = employee['name']
		attendance.employee_type = "Muster Roll"
		attendance.submit()
