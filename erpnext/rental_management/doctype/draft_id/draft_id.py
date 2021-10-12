# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DraftID(Document):
	def validate(self):
		pass

	def on_submit(self):
		frappe.db.sql ("update `tabTenant Information` set docstatus = 0 where name= '{0}' ".format(self.tenant_id))
