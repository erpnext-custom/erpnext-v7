# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MonthlyIndent(Document):
	def validate(self):	
		pass

	def on_submit(self):
		if not self.status == 'Completed':
			frappe.throw("Only Completed Monthly Indent can be Submitted.") 
