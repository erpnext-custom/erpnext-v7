# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ItemSubGroup(Document):
	def validate(self):
		if self.reading_required:
			if not self.reading_parameter:
				frappe.throw("Reading Parameter is Mandatory")
			if flt(self.minimum_value) > flt(self.maximum_value):
				frappe.throw("Invalid Min and Max Acceptable Values")
