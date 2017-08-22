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

class BOQ(Document):
	def validate(self):
                self.update_item_seq()                

        def update_item_seq(self):
                item_group = ""
                for item in self.boq_item:
                        if item.is_group:
                                item_group = item.item

                        item.parent_item = item_group

# Reference taken from `Timesheet`
@frappe.whitelist()
def make_project_invoice(source_name, target=None):
        frappe.msgprint(source_name)
        target = frappe.new_doc("Project Invoice")
        #set_missing_values(source_name, target)
        target.append("project_invoice_boq", get_mapped_doc("BOQ", source_name, {
                "BOQ Item": {
                        "doctype": "Project Invoice BOQ",
                        "field_map": {
                                "item": "item"
                        },
                }
        }))

        return target

def set_missing_values(boq, target):
        pass
