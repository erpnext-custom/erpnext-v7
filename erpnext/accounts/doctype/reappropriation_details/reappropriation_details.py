# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from erpnext.custom_autoname import get_auto_name

class ReappropriationDetails(Document):
	pass

	def autoname(self):
		self.name = make_autoname(get_auto_name(self, self.naming_series) + ".####")
