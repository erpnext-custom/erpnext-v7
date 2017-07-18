# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, nowdate, money_in_words
from frappe.model.mapper import get_mapped_doc

class BreakDownReport(Document):
	pass

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
