# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class VehicleLogbook(Document):
	def validate(self):
		self.check_duplicate()
		self.calculate_totals()

	def on_submit(self):
		self.update_hire()

	def check_duplicate(self):		
		for a in self.vlogs:
			for b in self.vlogs:
				if a.date == b.date and a.idx != b.idx:
					frappe.throw("Duplicate Dates in Vehicle Logs in row " + str(a.idx) + " and " + str(b.idx))
	def calculate_totals(self):
		if self.vlogs:
			total_w = total_i = 0
			for a in self.vlogs:
				total_w += flt(a.work_time)
				total_i += flt(a.idle_time)
			self.total_work_time = total_w
			self.total_idle_time = total_i

	def update_hire(self):
		if self.ehf_name:
			doc = frappe.get_doc("Equipment Hiring Form", self.ehf_name)
			doc.db_set("hiring_status", 1)
