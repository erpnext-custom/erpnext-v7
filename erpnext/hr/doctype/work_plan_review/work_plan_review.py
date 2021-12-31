# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import flt, getdate, cint

from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name

class WorkPlanReview(Document):
	def validate(self):
		if not self.status:
			self.status = "Draft"

		set_employee_name(self)
		self.validate_dates()
		self.check_total_points()
		self.validate_existing_work_plan_review()

	def get_employee_name(self):
		self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
		return self.employee_name
				
	def validate_dates(self):
		if getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("End Date can not be less than Start Date"))	

			##checking existing work plan review 
	def validate_existing_work_plan_review(self):
		chk = frappe.db.sql("""select name, start_date, end_date
			from `tabWork Plan Review`
			where employee = %(employee)s and docstatus < 2 and status in ("Draft", "Approved")
			and end_date >= %(start_date)s and start_date <= %(end_date)s
			and name != %(name)s""", {
				"employee": self.employee,
				"start_date": self.start_date,
				"end_date": self.end_date,
				"name": self.name
			})

		if chk:
			frappe.throw(_("Work Plan Review {0} created for Employee {1} in the given date range").format(chk[0][0], self.employee_name))				



			##checking the Task(work) weightage and add up the weightage % up to 100 %
	def check_total_points(self):
		total_points = 0
		for d in self.get("work_changes"):
			total_points += int(d.per_weightage or 0)

			## total weightage should except 0, or 100 in work plan changes
		if cint(total_points) not in (0, 100):
			frappe.throw(_("Sum of points for all weightage of work plan changes should be 100. It is {0}").format(total_points))	

		
			

	## fetch child table.
@frappe.whitelist()
def fetch_appraisal_work_plan(source_name, target_doc=None):
	doclist = get_mapped_doc("Appraisal Work Plan", source_name, {
		"Appraisal Work Plan": {
			"doctype": "Work Plan Review",
		},
		"Appraisal Plan Goal":{
			"doctype": "Appraisal Plan Goal",
		}

	}, target_doc)
	return doclist
			
	




			