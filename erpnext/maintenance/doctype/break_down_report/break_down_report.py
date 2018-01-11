# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, nowdate, money_in_words
from frappe.model.mapper import get_mapped_doc
from frappe.utils.data import add_years
from erpnext.custom_utils import check_uncancelled_linked_doc

class BreakDownReport(Document):
	def on_submit(self):
		self.assign_reservation()

	def on_cancel(self):
		docs = check_uncancelled_linked_doc(self.doctype, self.name)
                if docs != 1:
                        frappe.throw("There is an uncancelled <b>" + str(docs[0]) + "("+ str(docs[1]) +")</b> linked with this document")
		frappe.db.sql("delete from `tabEquipment Reservation Entry` where ehf_name = \'"+str(self.name)+"\'")
	
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
			doc.to_date = add_years(self.date, 1)
			doc.submit()

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
				"validation": {"docstatus": ["=", 1]}
			},
		}, target_doc)
	return doc
