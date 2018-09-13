# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_utils import get_cc_warehouse

class Production(Document):
	def validate(self):
		self.set_default_values()

	def set_default_values(self):
		obj = get_cc_warehouse(self.branch)
		self.warehouse = obj['wh']
		self.cost_center = obj['cc']

