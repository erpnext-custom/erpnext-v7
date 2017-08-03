# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document


class MusterRollAttendance(Document):
	pass


@frappe.whitelist()
def get_employees(date, project=None):
	attendance_not_marked = []
	attendance_marked = []
	employee_list = frappe.get_list("Muster Roll Employee", fields=["name", "person_name"], filters={
		"status": "Active", "project": project}, order_by="person_name")
	marked_employee = {}
	for emp in frappe.get_list("MR Attendance", fields=["muster_roll_employee", "status"],
							   filters={"date": date}):
		marked_employee[emp['muster_roll_employee']] = emp['status']

	for employee in employee_list:
		employee['status'] = marked_employee.get(employee['name'])
		if employee['name'] not in marked_employee:
			attendance_not_marked.append(employee)
		else:
			attendance_marked.append(employee)
	return {
		"marked": attendance_marked,
		"unmarked": attendance_not_marked
	}


@frappe.whitelist()
def mark_employee_attendance(employee_list, status, date, project, company=None):
	employee_list = json.loads(employee_list)
	for employee in employee_list:
		attendance = frappe.new_doc("MR Attendance")
		attendance.muster_roll_employee = employee['name']
		attendance.date = date
		attendance.project = project
		attendance.status = status
		attendance.submit()
