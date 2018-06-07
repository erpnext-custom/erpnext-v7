# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class SWSApplication(Document):
	def validate(self):
		self.validate_save()
		self.validate_dead()
		self.validate_amount()

	def validate_save(self):
		if not self.verified and self.approval_status == "Approved":
			frappe.throw("Can approve claim only after verification by supervisors")
				
	def validate_amount(self):
		total_amount = 0
		for a in self.items:
			if not a.amount:
				a.amount = a.claim_amount
			total_amount = flt(total_amount) + flt(a.amount)	
		self.total_amount = total_amount

	def validate_dead(self):
		for a in self.items:
			if a.dead:
				frappe.throw("The dependent is marked dead. Please contact HR Section")

	def on_submit(self):
		if self.total_amount <= 0:
			frappe.throw("Total Amount cannot be 0 or less")
		self.verify_approvals()
		self.update_status()
		self.post_sws_entry()
	
	def verify_approvals(self):
		if not self.verified:
			frappe.throw("Cannot submit unverified application")
		if self.approval_status != "Approved":
			frappe.throw("Can submit only Approved application")

	def update_status(self):
		for a in self.items:
			if frappe.db.get_value("SWS Event", a.sws_event, "dead"):
				doc = frappe.get_doc("Employee Family Details", a.reference_document)
				if self.docstatus == 1:
					doc.db_set("dead", 1)
				if self.docstatus == 2:
					doc.db_set("dead", 0)

	def post_sws_entry(self):
		doc = frappe.new_doc("SWS Entry")
		doc.flags.ignore_permissions = 1
		doc.posting_date = self.posting_date
		doc.branch = self.branch
		doc.ref_doc = self.name
		doc.employee = self.employee
		doc.debit = self.total_amount
		doc.submit()

	def on_cancel(self):
		self.update_status()
		self.delete_sws_entry()

	def delete_sws_entry(self):
		frappe.db.sql("delete from `tabSWS Entry` where ref_doc = %s", self.name)


