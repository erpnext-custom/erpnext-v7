# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from erpnext.custom_utils import sendmail, get_branch_cc, get_cc_customer
from frappe.utils import flt

class EquipmentRequest(Document):
	def validate(self):
		self.check_branch()
		self.calculate_percent()

	def check_branch(self):
		if self.branch == self.sbranch:
			frappe.throw("Requesting and Supplier Branch cannot be same.")

	def calculate_percent(self):
		total_item = len(self.items)
		per_item = flt(flt(100) / flt(total_item), 2)
		for a in self.items:
			a.percent_share = per_item 

	def on_submite(self):
		self.sendmailtorm()

	def sendmailtorm(self):
         	mails = frappe.db.sql("select email from `tabBranch Fleet Manager Item` where parent = %s", self.sbranch, as_dict=True)
	        for a in mails:
			message = "Equipment Request " + str(self.name) + " has been submitted to your office from " + str(self.branch)
			sendmail(recipients=a.email, sender=None, subject="Equipment Request Notification", message=message)

@frappe.whitelist()
def make_hire_form(source_name, target_doc=None):
        def update_hire_form(obj, target, source_parent):
                target.private = "CDCL"
                target.cost_center = get_branch_cc(obj.sbranch)
		target.customer = get_cc_customer(target.customer_cost_center)
		target.branch = obj.sbranch

        def update_item(obj, target, source_parent):
		target.from_time = "0:00"
		target.to_time = "0:00"
		target.total_hours = obj.total_hours 
		target.request_reference = obj.name
		target.equipment_request = source_parent.name

        def adjust_last_date(source, target):
                pass
                """target.items[len(target.items) - 1].dsa_percent = 50 
                target.items[len(target.items) - 1].actual_amount = target.items[len(target.items) - 1].actual_amount / 2
                target.items[len(target.items) - 1].amount = target.items[len(target.items) - 1].amount / 2"""

        doc = get_mapped_doc("Equipment Request", source_name, {
                        "Equipment Request": {
                                "doctype": "Equipment Hiring Form",
                                "field_map": {
                                        "sbranch": "branch",
                                        "branch": "customer_branch",
                                        "cost_center": "customer_cost_center",
                                },
                                "postprocess": update_hire_form,
                                "validation": {"docstatus": ["=", 1]}
                        },
                        "Equipment Request Item": {
                                "doctype": "Hiring Approval Details",
                                "field_map": {
                                },
                                "postprocess": update_item,
                                "validation": {"approved": ["=", 0]}
                        },
                }, target_doc, adjust_last_date)
        return doc

