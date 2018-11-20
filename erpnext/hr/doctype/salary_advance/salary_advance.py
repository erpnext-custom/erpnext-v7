# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt,cint,today,nowdate

class SalaryAdvance(Document):
	def validate(self):
		self.total_claim = self.basic_pay * self.months
		self.get_basic_pay()

	def get_basic_salary(self):
		if self.employee:
			sst_doc = frappe.get_doc("Salary Structure",frappe.db.get_value('Salary Structure', {'employee': self.employee, 'is_active' : 'Yes'}, "name"))
			for d in sst_doc.earnings:
				if d.salary_component == 'Basic Pay':
					self.basic_pay = flt(d.amount)
	
		
