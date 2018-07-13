# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import add_days

class FixedDeposit(Document):
	def validate(self):
		interest_amount = ((self.principal * (self.rate / 100.00)) / 365.00 ) * self.days
		if self.i_amount != interest_amount:
			self.i_amount = interest_amount
	
		tot_amount = interest_amount + self.principal
		if self.total_amount != tot_amount:
			self.total_amount = tot_amount
	
