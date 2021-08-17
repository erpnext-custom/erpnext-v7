# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe import _
from frappe.utils import flt
from frappe.utils import nowdate

class PMS(Document):
	def validate(self):
		self.validate_fields()
		self.check_weightage()
    
	def validate_fields(self):
		if not self.title:
			frappe.throw("<b>Title field cannot be blank</b>")
		if not self.department:
			frappe.throw("<b>Department field cannot be blank</b>")
		if not self.employee:
			frappe.throw("<b>Department Head field cannot be blank</b>")
		if not self.user:
			frappe.throw("<b>Approver field cannot be blank</b>")
   
		for i, t in enumerate(self.items):
			if not t.output:
				frappe.throw("<b>Output field cannot be blank</b>")
			if not t.success_indicator:
				frappe.throw("<b>Success Indicator(SI) field cannot be blank</b>")
			if t.weightage == "":
				frappe.throw("<b>Weightage field cannot be blank</b>")
			if not t.unit:
				frappe.throw("<b>Unit field cannot be blank</b>")
			if t.unit == "Date":
				if t.target_date < nowdate():
					frappe.throw(_("<b>The target date should not be before today's date"))
			elif t.unit == "Percentage":
				if flt(t.target_per) > 100:
					frappe.throw(_("<b>The target percentage can not be greater than 100</b>"))
				if flt(t.target_per) < 0:
					frappe.throw(_("<b>The target percentage can not be less than 0</b>"))
	
	def check_weightage(self):
		total_weightage = 0
 		for i, t in enumerate(self.items):
			if flt(t.weightage) <= 0:
				frappe.throw(_("<b>Value less than or equal to 0 is not allowed in TARGET SET UP at Row {}</b>".format(i+1)))
			elif  flt(t.weightage) > 100:
				frappe.throw(_("<b>Value cannot be greater than 100 in TARGET SET UP at Row {}</b>".format(i+1)))
			total_weightage += t.weightage	
         
		if total_weightage != 100:
			frappe.throw(_("<b>Sum of Weightage in TARGET SET UP must be 100</b>"))
	
@frappe.whitelist()
def create_evaluate(source_name, target_doc=None):
	doclist = get_mapped_doc("PMS", source_name, {
		"PMS": {
			"doctype": "PMS Evaluation"
		},
	}, target_doc)

	return doclist