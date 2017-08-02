# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class OvertimeApplication(Document):
	def validate(self):
		self.validate_dates()

	def on_submit(self):
		self.validate_submitter()

	##
	# Dont allow duplicate dates
	##
	def validate_dates(self):
		for a in self.items:
			for b in self.items:
				if a.date == b.date and a.idx != b.idx:
					frappe.throw("Duplicate Dates in row " + str(a.idx) + " and " + str(b.idx))

	##
	# Allow only the approver to submit the document
	##
	def validate_submitter(self):
		if self.approver != frappe.session.user:
			frappe.throw("Only the selected Approver can submit this document")

	
