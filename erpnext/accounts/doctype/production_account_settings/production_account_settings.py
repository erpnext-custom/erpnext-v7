# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ProductionAccountSettings(Document):
	def on_update(self):
		self.check_duplicate()

	def check_duplicate(self):
		for a in frappe.db.sql("select name from `tabProduction Account Settings` where company = %s and name != %s", (self.company, self.name), as_dict=1):
			frappe.throw("Production Account Settings already created for your Company")

