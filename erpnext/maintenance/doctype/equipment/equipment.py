# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class Equipment(Document):
	def before_save(self):
		for i, item in enumerate(sorted(self.operators, key=lambda item: item.start_date), start=1):
			item.idx = i

	def validate(self):
		if self.asset_code:
			doc = frappe.get_doc("Asset", self.asset_code)
			doc.db_set("equipment_number", self.name)

		if not self.equipment_number:
			self.equipment_number = self.name

	#def on_update(self):
		if len(self.operators) > 1:
			for a in range(len(self.operators)-1):
				self.operators[a].end_date = frappe.utils.data.add_days(getdate(self.operators[a + 1].start_date), -1)
			self.operators[len(self.operators) - 1].end_date = ''
		self.set_name()

	def set_name(self):
		for a in self.operators:
			if a.employee_type == "Employee":
				a.operator_name = frappe.db.get_value("Employee", a.operator, "employee_name")
			if a.employee_type == "Muster Roll Employee":
				a.operator_name = frappe.db.get_value("Muster Roll Employee", a.operator, "person_name")

	def validate_asset(self):
		if self.asset_code:
			equipments = frappe.db.sql("select name from tabEquipment where asset_code = %s and name != %s", (self.asset_code, self.name), as_dict=True)
			if equipments:
				frappe.throw("The Asset is already linked to another equipment")
	
@frappe.whitelist()
def get_yards(equipment):
	t, m = frappe.db.get_value("Equipment", equipment, ['equipment_type', 'equipment_model'])
	data = frappe.db.sql("select lph, kph from `tabHire Charge Parameter` where equipment_type = %s and equipment_model = %s", (t, m), as_dict=True)
	if not data:
		frappe.throw("Setup yardstick for " + str(m))
	return data

@frappe.whitelist()
def get_equipments(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("select a.equipment as name from `tabHiring Approval Details` a where docstatus = 1 and a.parent = \'"+ str(filters.get("ehf_name")) +"\'")

def sync_branch_asset():
	objs = frappe.db.sql("select e.name, a.branch from tabEquipment e, tabAsset a where e.asset_code = a.name and e.branch != a.branch", as_dict=True)
	for a in objs:
		frappe.db.sql("update tabEquipment set branch = %s where name = %s", (a.branch, a.name))





