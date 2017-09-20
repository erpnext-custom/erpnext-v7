# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DepartmentDirector(Document):
	def validate(self):
		dd = frappe.db.sql("select 1 from `tabDepartmentDirector` where docstatus = 1 and department = %s and name != %s", (self.department, self.name))
		if dd:
			frappe.throw("Director is already assgined for department " + str(self.department))
