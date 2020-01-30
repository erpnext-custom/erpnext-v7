# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Service(Document):
	def validate(self):
		self.item_code = self.name
		self.validate_region_rate()

	def validate_region_rate(self):
		if not self.same_rate:
			for a in frappe.db.sql("select region from `tabBSR Region`",as_dict=True):
				flag = 0
				for r in self.bsr_detail_item:
					if a.region == r.region:
						flag = 1
				if not flag:
					frappe.throw("BSR Rate missing for {0} Region".format(a.region) )
					
