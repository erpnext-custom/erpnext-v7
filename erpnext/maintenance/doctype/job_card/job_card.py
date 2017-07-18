# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class JobCard(Document):
	def validate(self):
		self.update_breakdownreport()

	def on_submit(self):
		self.post_journal_entry()
		self.update_breakdownreport()

	def before_cancel(self):
		cl_status = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if cl_status == 1:
			frappe.throw("You need to cancel the journal entry related to this job card first!")
		
		bdr = frappe.get_doc("Break Down Report", self.break_down_report)
		bdr.db_set("job_card", "")

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		pass

	##
	# Update the job card reference on Break Down Report
	##
	def update_breakdownreport(self):
		bdr = frappe.get_doc("Break Down Report", self.break_down_report)
		bdr.db_set("job_card", self.name)
