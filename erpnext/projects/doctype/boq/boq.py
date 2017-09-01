# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		                    2017/08/15         Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from frappe.utils import cstr, flt

class BOQ(Document):
        def autoname(self):
                self.name = make_autoname(str('BOQ')+'.YYYY.MM.####')
                
	def validate(self):
                self.update_defaults()

        def update_defaults(self):
                item_group = ""
                self.claimed_amount = 0
                self.received_amount = 0
                self.balance_amount = 0
                
                for item in self.boq_item:
                        if item.is_group:
                                item_group = item.item

                        item.parent_item = item_group
                        self.claimed_amount  += flt(item.claimed_amount)
                        self.received_amount += flt(item.received_amount)
                        self.balance_amount += (flt(item.amount)-flt(item.received_amount))
        
@frappe.whitelist()
def make_project_invoice(source_name, target_doc=None):
        def update_master(source_doc, target_doc, source_parent):
                target_doc.invoice_title = str(target_doc.project) + "(Project Invoice)"
                target_doc.check_all = 1
                
        def update_item(source_doc, target_doc, source_parent):
                target_doc.act_quantity = flt(target_doc.invoice_quantity)
                target_doc.act_rate     = flt(target_doc.invoice_rate)
                target_doc.act_amount   = flt(target_doc.invoice_amount)
                
        doclist = get_mapped_doc("BOQ", source_name, {
                "BOQ": {
                        "doctype": "Project Invoice",
                        "field_map": {
                                "project": "project"
                        },
                        "postprocess": update_master
                },

                "BOQ Item": {
                        "doctype": "Project Invoice BOQ",
                        "field_map": {
                                "name": "boq_item_name",
                                "balance_quantity": "invoice_quantity",
                                "rate": "invoice_rate",
                                "balance_amount": "invoice_amount"
                        },
                        "postprocess": update_item
                }
        }, target_doc)

        return doclist
