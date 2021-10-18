# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
class OpeningBRSEntry(Document):
	def validate(self):
		self.validate_amount()

	def validate_amount(self):
		for d in self.details:
			if(d.credit_amount > 0 and d.debit_amount > 0):
				frappe.throw(_("At Row {0} either Credit Amount should be 0 or Debit Amount should be 0 for party: {1}").format(d.idx, d.party))