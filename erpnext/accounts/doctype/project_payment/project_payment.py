# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# project_payment.py
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
	def __setup__(self):
                self.onload()
                
        def onload(self):
                if not self.get('__unsaved') and not self.get("references") and self.get("project"):
                        #self.load_references()
                        #self.load_advances()
                        pass

        def validate(self):
                self.validate_mandatory_fields()
                self.validate_allocated_amounts()
                #frappe.msgprint(_("{0}").format(self.get("project")))

        def validate_mandatory_fields(self):
                if not self.project:
                        frappe.throw("Project Cannot be null.")

                if not self.branch:
                        frappe.throw("Branch Cannot be null.")

                if not self.party:
                        frappe.throw("Customer Cannot be null.")

                for ded in self.deductions:
                       if not ded.account and flt(ded.amount) > 0:
                               frappe.throw(_("Row#{0} Account Cannot be null under `Other Deductions`.").format(ded.idx))

                if not self.tds_account and flt(self.tds_amount) > 0.0:
                        frappe.throw("TDS Account cannot be null.")

        def validate_allocated_amounts(self):
                tot_adv_amount = 0.0
                tot_inv_amount = 0.0
                
                for adv in self.advances:
                        tot_adv_amount += adv.allocated_amount

                for inv in self.references:
                        tot_inv_amount += inv.allocated_amount

                if flt(tot_adv_amount) > flt(tot_inv_amount):
                        frappe.throw(_("Total Advance Allocated({0}) cannot be more than Total Invoice Amount Allocated({1}).".format(flt(tot_adv_amount), flt(tot_inv_amount))))

                if flt(self.total_amount) > flt(tot_inv_amount):
                        frappe.throw(_("Total Amount({0}) cannot be more than Total Invoice Amount Allocated({1})").format(flt(self.total_amount),flt(tot_inv_amount)))
                        
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

        

# ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++        
# Following method is created by SHIV on 05/09/2017
@frappe.whitelist()
def make_project_payment(source_name, target_doc=None):
        def update_master(source_doc, target_doc, source_partent):
                #target_doc.project = source_doc.project
                pass

        def update_reference(source_doc, target_doc, source_parent):
                pass
                
        doclist = get_mapped_doc("Project Invoice", source_name, {
                "Project Invoice": {
                                "doctype": "Project Payment",
                                "field_map":{
                                        "project": "project",
                                        "branch": "branch",
                                        "customer": "customer",
                                        "name": "reference_name"
                                },
                                "postprocess": update_master
                        },
        }, target_doc)
        return doclist

@frappe.whitelist()
def get_invoice_list(project, reference_name):
        if reference_name == "dummy":
                reference_name = None
                
        result = frappe.db.sql("""
                select *
                from `tabProject Invoice`
                where project = %s
                and docstatus = 1
                and total_balance_amount > 0
                and name = ifnull(%s,name)
                """, (project, reference_name), as_dict=True)

        return result

@frappe.whitelist()
def get_advance_list(project):
        result = frappe.db.sql("""
                select *
                from `tabProject Advance`
                where project = %s
                and docstatus = 1
                and balance_amount > 0
                """, (project), as_dict=True)

        return result

# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
