# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate

from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name

class EmployeeAppraisal(Document):
	def validate(self):
		if not self.status:
			self.status = "Draft"

		set_employee_name(self)
		self.validate_dates()
		self.validate_existing_employee_appraisal()
		self.calculate_total()

	def get_employee_name(self):
		self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
		return self.employee_name

	def validate_dates(self):
		if getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("End Date can not be less than Start Date"))


	def validate_existing_employee_appraisal(self):
		
		chk = frappe.db.sql("""select name, start_date, end_date
			from `tabEmployee Appraisal`
			where employee = %(employee)s and docstatus < 2 and status in ("Draft", "Accepted")
			and end_date >= %(start_date)s and start_date <= %(end_date)s
			and name != %(name)s""", {
				"employee": self.employee,
				"start_date": self.start_date,
				"end_date": self.end_date,
				"name": self.name
			})

		if chk:
			frappe.throw(_("Employee Appraisal {0} created for Employee {1} in the given date range").format(chk[0][0], self.employee_name))	

	def calculate_total(self):
		total, total_w = 0, 0
		for d in self.get("goals"):
			if d.score:
				total = total + d.score_earned
				total_w += flt(d.per_weightage) 


		
		if frappe.db.get_value("Employee", self.employee, "user_id") != \
				frappe.session.user and total == 0:
			frappe.throw(_("Total cannot be zero"))
		self.self_score = total			

@frappe.whitelist()
def fetch_work_plan_review(source_name, target_doc=None):
	doclist = get_mapped_doc("Work Plan Review", source_name, {
		"Work Plan Review": {
			"doctype": "Employee Appraisal",
		},
		"Appraisal Plan Goal":{
			"doctype": "Appraisal Plan Goal",
		},
		"Appraisal Plan Goals":{
			"doctype": "Appraisal Plan Goals",
		}
	}, target_doc)
	return doclist
	

@frappe.whitelist()
def fetch_appraisal_template(source_name, target_doc=None):
	doclist = get_mapped_doc("Appraisal Template", source_name, {
		"Appraisal Template": {
			"doctype": "Employee Appraisal",
		},
		"Rating Guide Template": {
			"doctype": "Rating Guide Template",
		},

		"Appraisal Template Goal":{
			"doctype": "Appraisal Goal",

		},

		"Appraisal Template Goals":{
			"doctype": "Appraisal Goals",
		},

		"Rating Template":{
			"doctype": "Appraisal Rating",
		},
		"Review Question": {
			"doctype" : "Review Question",
		},

		"Review Discussion": {
			"doctype": "Review Discussion",
		}
	}, target_doc)
	return doclist

#@frappe.whitelist()
#def fetch_appraisal_training(source_name, target_doc=None):
#	doclist = get_mapped_doc("Employee Appraisal", source_name, {
#		
#		"Appraisal Training": {
#			"doctype": "Employee Appraisal",
#		}
#	}, target_doc)
#	return doclist


			
	
