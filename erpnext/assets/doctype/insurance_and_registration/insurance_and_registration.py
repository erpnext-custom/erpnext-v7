# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

class InsuranceandRegistration(Document):
	def validate(self):
		self.validate_insuranced()
		self.posting_date = self.in_items[-1].due_date

	def validate_insuranced(self):
		insured_list = frappe.db.sql("""select name, insurance_type from `tabInsurance and Registration` """, as_dict =1)
		for a in insured_list:
			if self.insurance_type == a.insurance_type:
				if self.name != a.name:
					frappe.throw ("Insurance and Registration transaction of the {0} is already saved in {1} document".format(self.insurance_type, a.name))


			
#		insured_date = frappe.db.get_all("Insurance Details", order_by="due_date", filters = {"parent": self.name, },fields={"name","due_date"})
		
