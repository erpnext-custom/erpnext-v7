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

		for a in self.items:
			if flt(a.lower_rate) <= 0 or flt(a.higher_rate) <= 0:
				frappe.throw("Rate cannot be smaller than 0 for row {0}".format(frappe.bold(a.idx)))

			if not cint(a.threshold_trip) > 0:
				frappe.throw("Threshold Trip should be greater than 0 for row {0}".format(frappe.bold(a.idx)))

			if flt(a.unloading_rate) <= 0:
				frappe.throw("Unloading Rate should be greater than 0 for row {0}".format(frappe.bold(a.idx)))

	def check_duplicate(self):
		for a in frappe.db.sql("select name from `tabTransporter Rate` where receiving_warehouse = %s and (%s between from_date and to_date or %s between from_date and to_date or (%s < from_date and %s > to_date)) and name != %s and equipment_type = %s",(self.receiving_warehouse, self.from_date, self.to_date, self.from_date, self.to_date, self.name, self.equipment_type) ,as_dict=1):
			frappe.throw("Cannot define overlapping rate settings")

		for a in frappe.db.sql("select item_code from `tabTransporter Rate Item` where parent = %s group by item_code having count(1) > 1", self.name, as_dict=1):
			frappe.throw("Cannot have different rate settings for item {0}".format(frappe.bold(a.item_code)))

def get_transporter_rate(warehouse, date, equipment_type, item_code):
	for d in frappe.db.sql("select a.name, b.threshold_trip, b.lower_rate, b.higher_rate, b.unloading_rate from `tabTransporter Rate` a, `tabTransporter Rate Item` b  where a.name = b.parent and  %s between a.from_date and a.to_date and a.receiving_warehouse = %s and a.equipment_type = %s and b.item_code = %s", (date, warehouse, equipment_type, item_code), as_dict=1):
		return {"name": d.name, "lower_rate": d.lower_rate, "higher_rate": d.higher_rate, "unloading_rate": d.unloading_rate, "threshold_trip": d.threshold_trip}
	frappe.throw("No Transporter rate Defined for {0} and Equipment Type {1}".format(frappe.bold(warehouse), frappe.bold(equipment_type)))


