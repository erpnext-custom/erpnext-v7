# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class ConsolidationTransaction(Document):
	pass

@frappe.whitelist()
def make_adjustment_entry(source_name, target_doc=None):
        
        doclist = get_mapped_doc("Consolidation Transaction", source_name, {
                "Consolidation Transaction": {
						"doctype": "Consolidation Adjustment Entry",
						"field_map":{
								"name": "consolidation_transaction"
						},
                        }
        }, target_doc)
        return doclist