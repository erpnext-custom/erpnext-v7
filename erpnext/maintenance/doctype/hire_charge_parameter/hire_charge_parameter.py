# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class HireChargeParameter(Document):
	def before_save(self):
		for i, item in enumerate(sorted(self.items, key=lambda item: item.from_date), start=1):
			item.idx = i

	def validate(self):
		self.db_set("without_fuel", self.items[len(self.items) - 1].rate_wofuel)	
		self.db_set("with_fuel", self.items[len(self.items) - 1].rate_fuel)	
		self.db_set("idle", self.items[len(self.items) - 1].idle_rate)	
		self.db_set("lph", self.items[len(self.items) - 1].yard_hours)	
		self.db_set("kph", self.items[len(self.items) - 1].yard_distance)	
		self.db_set("benchmark", self.items[len(self.items) - 1].perf_bench)	
		self.db_set("interval", self.items[len(self.items) - 1].main_int)

	
