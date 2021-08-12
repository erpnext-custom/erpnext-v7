# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DepartmentalGroup(Document):
	def validate(self):
		self.validate_min_labor()
		
	def validate_min_labor(self):
		if self.tire == 'Tire 1- Bhutanese' or self.tire == 'Tire 2-Indian':
			if not self.minimum_labor:
				frappe.throw("Minimum Labours is Require")
