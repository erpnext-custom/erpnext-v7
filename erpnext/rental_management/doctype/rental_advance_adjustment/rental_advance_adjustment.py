# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, nowtime, getdate, nowdate

class RentalAdvanceAdjustment(Document):
	def validate(self):
		self.update_advance_details()

	def update_advance_details(self):
		total_advance_received = total_advance_adjusted = 0.00
		
		if self.advance_received_item:
			for a in self.advance_received_item:
				total_advance_received += flt(a.balance_amount)

		if self.advance_adjusted_item:
			for a in self.advance_adjusted_item:
				total_advance_adjusted += flt(a.adjusted_amount)

		self.advance_received = flt(total_advance_received)
		self.advance_adjusted = flt(total_advance_adjusted)

		if self.advance_received > 0:
			self.advance_balance = flt(self.advance_received) - flt(self.advance_adjusted)

			
