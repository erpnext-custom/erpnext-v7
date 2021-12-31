# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, getdate, cint

from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
#from erpnext.hr.utils import set_letter_index
from erpnext.hr.utils import set_employee_name

class OfficialDocument(Document):
	def validate(self):

		set_employee_name(self)
		#set_letter_index(self)



	def get_employee_name(self):
		self.get_employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
		return self.employee_name

	def get_letter_index(self):
		self.get_letter_index = frappe.db.get_value("DocumentTemplate", self.document_type, "letter_index")
		return self.letter_index
