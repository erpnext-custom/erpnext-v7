# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class POLIssueReport(Document):
	def validate(self):
		if not self.items:
			frappe.throw("Should have a POL Issue Details to Submit")

	def on_submit(self):
		self.consume_pol()

	def consume_pol(self):
		for a in self.items:
			con = frappe.new_doc("Consumed POL")	
			con.equipment = a.equipment
			con.branch = self.branch
			con.pol_type = a.pol_type
			con.date = self.date
			con.qty = a.qty
			con.submit()

