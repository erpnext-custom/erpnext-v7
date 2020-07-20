# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
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
		for i in self.get("items"):
			for a in frappe.db.sql("""select t.name 
					from `tabTransporter Rate` t, `tabTransporter Rate Item` ti
					where t.from_warehouse = %s 
					and t.receiving_warehouse = %s 
					and (
						(%s between t.from_date and t.to_date) or 
						(%s between t.from_date and t.to_date) or 
						(%s <= t.to_date and %s >= t.from_date)) 
					and t.name != %s 
					and ti.parent = t.name
					and ti.equipment_type = %s
					and ti.item_code = %s
				""",(self.from_warehouse, self.receiving_warehouse, self.from_date, self.to_date, self.from_date, 
					self.to_date, self.name, i.equipment_type, i.item_code) ,as_dict=1):
				frappe.throw(_("Rate already defined via {}").format(frappe.get_desk_link('Transporter Rate', a.name), title="Duplicate Entry"))

		'''
		for a in frappe.db.sql("""select item_code from `tabTransporter Rate Item` 
				where parent = %s group by item_code having count(1) > 1""", self.name, as_dict=1):
			frappe.throw("Cannot have different rate settings for item {0}".format(frappe.bold(a.item_code)))
		'''

		dup = frappe._dict()
		for i in self.get("items"):
			if i.equipment_type in dup:
				if i.item_code in dup.get(i.equipment_type):
					frappe.throw(_("Row#{}: Duplicate entry for item {} under Equipment Type {}")\
						.format(i.idx, frappe.bold(i.item_code), frappe.bold(i.equipment_type)))
				else:
					dup.setdefault(i.equipment_type, []).append(i.item_code)
			else:
				dup.setdefault(i.equipment_type, []).append(i.item_code)

def get_transporter_rate(from_warehouse, receiving_warehouse, date, equipment_type, item_code):
	rate = frappe.db.sql("""select a.name, b.threshold_trip, b.lower_rate, b.higher_rate, 
				b.unloading_rate, a.expense_account 
			from `tabTransporter Rate` a, `tabTransporter Rate Item` b  
			where a.from_warehouse = %s
			and a.receiving_warehouse = %s 
			and %s between a.from_date and a.to_date 
			and a.name = b.parent 
			and b.item_code = %s
			and b.equipment_type = %s 
		""", (from_warehouse, receiving_warehouse, date, item_code, equipment_type), as_dict=True)
		
	if not rate:
		frappe.throw(_("""No Transporter Rate defined between source warehouse {} and receiving warehouse {}
					for Equipment Type {} and  Material {} for the date {}""")\
				.format(frappe.bold(from_warehouse), frappe.bold(receiving_warehouse), 
					frappe.bold(equipment_type), frappe.bold(item_code), frappe.bold(date)),title="No Data Found")

	return rate[0]

