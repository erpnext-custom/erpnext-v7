# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states
from frappe.model.mapper import get_mapped_doc

class OvertimeAuthorization(Document):
	def validate(self):
		validate_workflow_states(self)





@frappe.whitelist()
def make_overtime_claim(source_name, target_doc=None):
        doclist = get_mapped_doc("Overtime Authorization", source_name, {
                "Overtime Authorization": {
                        "doctype": "Overtime Claim",
                        "field_map": {
                                "parent": "name",
                        },
                        "validation": {
                                "docstatus": ["=", 1]
                        }
                },
        }, target_doc)

        return doclist
