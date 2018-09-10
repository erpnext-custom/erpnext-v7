# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BusinessActivity(Document):
	def validate(self):
		if self.is_default:
			def_ba = frappe.db.sql("select name from `tabBusiness Activity` where is_default = 1", as_dict=1)
			for a in def_ba:
				frappe.throw(str(a.name) + " is already set as default. Unset and Save again")

def get_default_ba():
	default_ba = frappe.db.sql("select name from `tabBusiness Activity` where is_default = 1", as_dict=1)
	default_ba = default_ba and default_ba[0].name or None	
	return default_ba	
