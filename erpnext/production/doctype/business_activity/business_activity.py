# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BusinessActivity(Document):
	def validate(self):
		found = []
		for a in self.get('items'):
			if  a.item in found:
				frappe.throw("Item {0} already added".format(a.item))
			else:
				found.append(a.item)
		
