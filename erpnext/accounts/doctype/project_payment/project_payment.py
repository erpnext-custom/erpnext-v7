# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  SHIV		                   05/09/2017         Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, getdate, get_url
from frappe.model.mapper import get_mapped_doc

class ProjectPayment(Document):
        def onload(self):
                if not self.get('__unsaved') and not self.get("references") and self.get("project"):
                        self.load_references()
                        self.load_advances()

	def __setup__(self):
                self.onload()


        def load_references(self):
                self.references = []
                for invoice in self.get_references():
                        self.append("references",{
                                "reference_doctype": "Project Invoice",
                                "reference_name": invoice.name,
                                "total_amount": invoice.total_balance_amount
                        })

        def load_advances(self):
                self.advances = []
                for advance in self.get_advances():
                        self.append("advances",{
                                "reference_doctype": "Project Advance",
                                "reference_name": advance.name,
                                "total_amount": advance.balance_amount
                        })


        def get_references(self):
                return frappe.get_all("Project Invoice","*",filters={"project":self.project, "docstatus":1, "total_balance_amount": [">",0]})

        def get_advances(self):
                return frappe.get_all("Project Advance","*",filters={"project":self.project, "docstatus":1, "balance_amount": [">",0]})

        
# Following method is created by SHIV on 05/09/2017
@frappe.whitelist()
def make_project_payment(source_name, target_doc=None):
        def update_master(source_doc, target_doc, source_partent):
                #target_doc.project = source_doc.project
                pass
        
        doclist = get_mapped_doc("Project Invoice", source_name, {
                "Project Invoice": {
                                "doctype": "Project Payment",
                                "field_map":{
                                        "project": "project",
                                        "branch": "branch",
                                        "customer": "customer",
                                        
                                },
                                "postprocess": update_master
                        }
        }, target_doc)
        return doclist
# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
