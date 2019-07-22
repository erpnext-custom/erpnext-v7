# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TrainingRecords(Document):
	def validate(self):
		self.check_double_entry()
		if not self.get("participants"):
			frappe.msgprint("Participants List Cannot Be Empty")
		if self.country == 'Bhutan' and not self.dzongkha:
			frappe.msgprint("Dzongkha/District is not selected")
	
        def on_submit(self):
		self.create_training_record()	

	def on_cancel(self):
        	self.delete_entries()

	def create_training_record(self):
                for emp in self.get("participants"):
                        emp_obj = frappe.get_doc("Employee", emp.employee)
                        emp_obj.flags.ignore_permissions = 1
                        emp_obj.append("training_and_development",{
                                                        "employee": emp.employee,
                                                        "training_type": self.training_type,
                                                        "location_type": self.location_type,
                                                        "start_date": self.start_date,
                                                        "end_date": self.end_date,
                                                        "ref_doc": self.name
                                })
                        emp_obj.save()	

	def check_double_entry(self):
		found = []
                for emp in self.get("participants"):
                        if emp.employee in found:
                                frappe.throw("Employee <b> '{0}' </b> Already Added In The List".format(emp.employee))
                        found.append(emp.employee)

	def delete_entries(self):
                frappe.db.sql("delete from `tabTraining History` where ref_doc = %s", self.name)
