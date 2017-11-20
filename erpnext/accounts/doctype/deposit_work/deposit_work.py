# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class DepositWork(Document):
	def validate(self):
		expense = received = 0
		for a in self.r_items:
			received += flt(a.amount)

		for d in self.e_items:
			expense += flt(d.amount)

		self.total_received_amount = received
		self.total_expense_amount = expense
		self.balance_amount = flt(received) - flt(expense)		

