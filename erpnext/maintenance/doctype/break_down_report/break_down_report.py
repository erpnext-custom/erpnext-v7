# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, nowdate, money_in_words
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import add_years
from erpnext.custom_utils import check_uncancelled_linked_doc, check_future_date

class BreakDownReport(Document):
	def validate(self):
		check_future_date(self.date)
		self.validate_equipment()

	def on_submit(self):
		self.assign_reservation()
		self.post_equipment_status_entry()

	def on_cancel(self):
		check_uncancelled_linked_doc(self.doctype, self.name)
		frappe.db.sql("delete from `tabEquipment Reservation Entry` where ehf_name = \'"+str(self.name)+"\'")
		frappe.db.sql("delete from `tabEquipment Status Entry` where ehf_name = \'"+str(self.name)+"\'")
	
	def validate_equipment(self):
		if self.owned_by in ['CDCL', 'Own']:
			eb = frappe.db.get_value("Equipment", self.equipment, "branch")
			if self.owned_by == "Own" and self.branch != eb:
				frappe.throw("Equipment <b>" + str(self.equipment) + "</b> doesn't belong to your branch")
			if self.owned_by == "CDCL" and self.customer_branch != eb:
				frappe.throw("Equipment <b>" + str(self.equipment) + "</b> doesn't belong to <b>" + str(self.customer_branch) + "</b>")
			if self.owned_by == "CDCL" and self.cost_center == self.customer_cost_center:
				frappe.throw("Equipment From your Branch should be 'Own' and not 'CDCL'")
		else:
			self.equipment = ""

	def assign_reservation(self):
		if self.owned_by in ['CDCL', 'Own']:
			doc = frappe.new_doc("Equipment Reservation Entry")
			doc.flags.ignore_permissions = 1 
			doc.equipment = self.equipment
			doc.reason = "Maintenance"
			doc.ehf_name = self.name
			doc.hours = 100
			doc.place = self.branch
			doc.from_date = self.date
			doc.from_time = self.time
			doc.to_date = add_years(self.date, 1)
			doc.submit()

	def post_equipment_status_entry(self):
		if self.owned_by in ['CDCL', 'Own']:
			ent = frappe.new_doc("Equipment Status Entry")
			ent.flags.ignore_permissions = 1 
			ent.equipment = self.equipment
			ent.reason = "Maintenance"
			ent.ehf_name = self.name
			ent.hours = 100
			ent.place = self.branch
			ent.from_date = self.date
			ent.from_time = self.time
			ent.to_date = add_years(self.date, 1)
			ent.submit()

@frappe.whitelist()
def make_job_card(source_name, target_doc=None): 
	def update_date(obj, target, source_parent):
		target.posting_date = nowdate()
	
	doc = get_mapped_doc("Break Down Report", source_name, {
			"Break Down Report": {
				"doctype": "Job Card",
				"field_map": {
					"name": "job_card",
					"date": "break_down_report_date"
				},
				"postprocess": update_date,
				"validation": {"docstatus": ["=", 1], "job_card": ["is", None]}
			},
		}, target_doc)
	return doc
