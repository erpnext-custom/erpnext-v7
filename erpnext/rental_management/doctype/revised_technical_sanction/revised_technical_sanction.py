# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, fmt_money, formatdate, nowdate

class RevisedTechnicalSanction(Document):
	def validate(self):
		self.calculate_total_amount()

	def calculate_total_amount(self):
		total = 0
		if self.items: 
			for item in self.items:
				total += item.total

		self.total_amount = total - self.tools_and_plant - self.rm

	def on_submit(self):
		if self.technical_sanction:
			frappe.db.sql("update `tabTechnical Sanction` set revised_technical_sanction = '{rts}' where name ='{ts}'".format(rts=self.name, ts=self.technical_sanction))
		else: 
			frappe.throw("There is no technical sanction {}".format(self.technical_sanction))

	def on_cancel(self):
		if self.docstatus == 2:
			frappe.db.sql("update `tabTechnical Sanction` set revised_technical_sanction = '' where name ='{ts}'".format(ts=self.technical_sanction))




@frappe.whitelist()
def prepare_bill(source_name, target_doc=None):
	def update_docs(obj, target, source_parent):
		target.revised_technical_sanction = obj.name
        doc = get_mapped_doc("Revised Technical Sanction", source_name, {
                        "Revised Technical Sanction": {
                                "doctype": "Technical Sanction Bill","field_map":{
									"total_amount" : "total_gross_amount"
								},	
                                "postprocess": update_docs,
                                "validation": {"docstatus": ["=", 1]}
                        },
                }, target_doc)
        return doc
