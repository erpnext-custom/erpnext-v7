# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Equipment(Document):
	def validate(self):
		if self.asset_code:
			doc = frappe.get_doc("Asset", self.asset_code)
			doc.db_set("equipment_number", self.name)

		if not self.equipment_number:
			self.equipment_number = self.name

@frappe.whitelist()
def get_yards(equipment):
	t, m = frappe.db.get_value("Equipment", equipment, ['equipment_type', 'equipment_model'])
	data = frappe.db.sql("select lph, kph from `tabHire Charge Parameter` where equipment_type = %s and equipment_model = %s", (t, m), as_dict=True)
	if not data:
		frappe.throw("Setup yardstick for " + str(m))
	return data

@frappe.whitelist()
def get_equipments(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("select a.equipment as name from `tabHiring Approval Details` a where a.parent = \'"+ str(filters.get("ehf_name")) +"\'")
