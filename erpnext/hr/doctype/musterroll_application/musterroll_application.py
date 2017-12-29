# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MusterRollApplication(Document):
	def validate(self):
		pass
	
	def on_submit(self):
		self.validate_submitter()
		self.check_status()
		self.create_mr()

	def validate_submitter(self):
		if self.approver != frappe.session.user:
			frappe.throw("Only the selected supervisor can submit this document")

	def check_status(self):
		for a in self.items:
			if not a.approver_status:
				frappe.throw("Approval Status cannot be empty for <b>" + str(a.citizenship_id) + "</b>")	

	def create_mr(self):
		for a in self.items:
			if a.approver_status == 'Approved':
				cur = frappe.db.get_value("Muster Roll Employee", a.citizenship_id, "name")
				if cur:
					doc = frappe.get_doc("Muster Roll Employee", a.citizenship_id)
				else:
					doc = frappe.new_doc("Muster Roll Employee")
					
				doc.person_name = a.person_name
				doc.status = 'Active'
				doc.branch = self.branch
				doc.cost_center = self.cost_center
				doc.joining_date = a.joining_date
				doc.rate_per_day = a.rate_per_day
				doc.rate_per_hour = a.rate_per_hour
				doc.company = "Construction Development Corporation Ltd"
				doc.id_card = a.citizenship_id
				if self.project:
					doc.project = self.project
				doc.save()
	
				 
