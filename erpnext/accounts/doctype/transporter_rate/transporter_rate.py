# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint

class TransporterRate(Document):
	def validate(self):
		self.check_data()

	def on_update(self):
		self.check_duplicate()

	def check_data(self):
		if self.from_date > self.to_date:
			frappe.throw("From Date cannot be greater than To Date")

		if flt(self.lower_rate) <= 0 or flt(self.higher_rate) <= 0:
			frappe.throw("Rate cannot be smaller than 0")

		if not cint(self.threshold_trip) > 0:
			frappe.throw("Threshold Trip should be greater than 0")

		if flt(self.unloading_rate) <= 0:
			frappe.throw("Unloading Rate should be greater than 0")

	def check_duplicate(self):
		for a in frappe.db.sql("select name from `tabTransporter Rate` where receiving_warehouse = %s and (%s between from_date and to_date or %s between from_date and to_date or (%s < from_date and %s > to_date)) and name != %s",(self.receiving_warehouse, self.from_date, self.to_date, self.from_date, self.to_date, self.name) ,as_dict=1):
			frappe.throw("Cannot define overlapping rate settings")

def get_transporter_rate(warehouse, date):
	for d in frappe.db.sql("select name from `tabTransporter Rate` where %s between from_date and to_date and receiving_warehouse = %s", (date, warehouse), as_dict=1):
		return frappe.get_doc("Transporter Rate", d.name)
	frappe.throw("No Transporter rate Defined for {0}".format(frappe.bold(warehouse)))


