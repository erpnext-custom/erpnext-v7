# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ProductionSettings(Document):
	def validate(self):
		self.check_percent_total()

	def check_percent_total(self):
		if flt(self.log_percent_conifer) + flt(self.firewood_percent_conifer) != 100:
			frappe.throw("Total of Conifer Perents should be 100")

		if flt(self.log_percent_broadleaf) + flt(self.firewood_percent_broadleaf) != 100:
			frappe.throw("Total of Broadleaf Perents should be 100")

	def on_update(self):
		self.check_duplicate()

	def check_duplicate(self):
		for a in frappe.db.sql("select name from `tabProduction Settings` where company = %s and name != %s", (self.company, self.name), as_dict=1):
			frappe.throw("Production Settings already created for your Company")


