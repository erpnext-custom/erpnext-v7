# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint

class ProductionSettings(Document):
	def validate(self):
		self.check_percent_total()
		self.check_duplicate()

	def check_percent_total(self):
		total_percent = 0
		for a in self.item:
			total_percent += a.ratio
			
		if cint(total_percent) > 100:
			frappe.throw("Total percent is {}. It should not be more than 100".format(total_percent))

	def check_duplicate(self):
		for a in frappe.db.sql("""
				select name from `tabProduction Settings`
				where branch = '{0}'
				and (
					from_date between '{1}' and '{2}'
					or ifnull(to_date, now()) between '{1}' and '{2}'
					or '{1}' between from_date and ifnull(to_date,now())
					or '{2}' between from_date and ifnull(to_date,now())
					)
				and raw_material = '{3}'
				and name != '{4}'
				and warehouse = '{5}'
			""".format(self.branch, self.from_date, self.to_date, self.raw_material, self.name, self.warehouse), as_dict=True):
			if a.name:
				frappe.throw("Production Setting already exists for {} within {} and {} date in {}".format(self.raw_material, self.from_date, self.to_date, a.name))
			


