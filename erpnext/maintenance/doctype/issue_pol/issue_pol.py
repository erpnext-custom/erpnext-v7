# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class IssuePOL(Document):
	def validate(self):
		if not self.items:
			frappe.throw("Should have a POL Issue Details to Submit")

	def on_submit(self):
		self.consume_pol()

	def on_cancel(self):
		self.cancel_consumed_pol()

	def consume_pol(self):
		for a in self.items:
			con = frappe.new_doc("Consumed POL")	
			con.equipment = a.equipment
			con.branch = self.branch
			con.pol_type = self.pol_type
			con.date = self.date
			con.qty = a.qty
			con.reference_type = "Issue POL"
			con.reference_name = self.name
			con.submit()
	
	def cancel_consumed_pol(self):
		frappe.db.sql("update `tabConsumed POL` set docstatus = 2 where reference_type = 'Issue POL' and reference_name = %s", (self.name))
