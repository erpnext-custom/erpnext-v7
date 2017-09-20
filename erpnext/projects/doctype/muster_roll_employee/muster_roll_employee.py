# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MusterRollEmployee(Document):
	def validate(self):
		self.calculate_rates()
		#self.check_status()

	def calculate_rates(self):
		if not self.rate_per_hour:
			self.rate_per_hour = (flt(self.rate_per_day) * 1.5) / 8

	def check_status(self):
		if self.status == "Left":
			self.cost_center = ''
			self.branch = ''
			self.project = ''
