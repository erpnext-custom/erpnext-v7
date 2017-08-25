# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AssignBranch(Document):
	def validate(self):
		self.check_duplicate()

	def on_update(self):
		frappe.msgprint("Updating......")

	def check_duplicate(self):		
		for a in self.items:
			for b in self.items:
				if a.branch == b.branch and a.idx != b.idx:
					frappe.throw("Duplicate Entries in row " + str(a.idx) + " and " + str(b.idx))


