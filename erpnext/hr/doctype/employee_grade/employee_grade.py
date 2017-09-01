# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class EmployeeGrade(Document):
	def validate(self):
		if flt(self.increment) > 0 and flt(self.increment_percent) > 0:
			frappe.throw("Cannot have both percent and lumpsum amount for increment")
