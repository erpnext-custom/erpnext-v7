# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Activity(Document):
	def validate(self):
		if not self.get('items'):
			frappe.throw("Item Cannot Be Empty")
