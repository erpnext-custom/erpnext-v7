# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class CoalRaisingMaster(Document):
	def validate(self):
		self.validate_field()
	def validate_field(self):
		if self.from_date > self.to_date:
			frappe.throw("From date cannot be before than to date")
