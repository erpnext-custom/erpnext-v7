# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, date_diff, nowdate

class StandardSawnBalance(Document):
	def validate(self):
		size = frappe.db.get_value("Standard Sawn Size", self.size, "value")
		length = frappe.db.get_value("Standard Sawn Size", self.length, "value")
		self.unit_cft = flt((size * length)/144)
		self.total_cft = flt(self.qty) * flt(self.unit_cft)
		self.balance_cft = flt(self.balance_qty) * flt(self.unit_cft)
		if self.balance_qty == None or self.balance_qty == "":
			self.balance_qty = self.qty
			if self.balance_cft == None or self.balance_cft == 0.0:
				self.balance_cft = flt(self.balance_qty) * flt(self.unit_cft)
