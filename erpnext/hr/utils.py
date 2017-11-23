# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def set_employee_name(doc):
	if doc.employee:
		emp = frappe.get_doc("Employee", doc.employee)
		doc.employee_name = emp.employee_name
		doc.designation = emp.designation
		doc.branch = emp.branch
		doc.department = emp.department
		doc.division = emp.division

