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
from frappe.utils import flt, getdate, get_url, nowdate
from frappe.model.mapper import get_mapped_doc
from frappe.utils import money_in_words
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import generate_receipt_no

class ProjectPayment(AccountsController):
	def __setup__(self):
                self.onload()
                
        def onload(self):
                if not self.get('__unsaved') and not self.get("references") and self.get("project"):
                        #self.load_references()
                        #self.load_advances()
                        pass

        def on_update(self):
                self.validate_invoice_balance()
                self.validate_advance_balance()

        def validate(self):
                self.set_status()
                self.set_defaults()
                self.validate_mandatory_fields()
                self.validate_allocated_amounts()
                #frappe.msgprint(_("{0}").format(self.get("project")))

        def on_submit(self):
                self.update_invoice_balance()
                self.update_advance_balance()                
                self.update_boq_balance()
                if str(self.posting_date) > '2017-09-30':
                        self.make_gl_entries()

        def before_cancel(self):
                self.set_status()

        def on_cancel(self):
                if str(self.posting_date) > '2017-09-30':
                        self.make_gl_entries()
                self.update_invoice_balance()
                self.update_advance_balance()
                self.update_boq_balance()
                
        def set_status(self):
                self.status = {
                        "0": "Draft",
                        "1": "Payment Received",
                        "2": "Cancelled"
                }[str(self.docstatus or 0)]

        def set_defaults(self):
                if self.project:
                        base_project          = frappe.get_doc("Project", self.project)
                        self.company          = base_project.company
                        self.party            = base_project.customer
                        self.branch           = base_project.branch
                        self.cost_center      = base_project.cost_center

                        if base_project.status in ('Completed','Cancelled'):
                                frappe.throw(_("Operation not permitted on already {0} Project.").format(base_project.status),title="Project Payment: Invalid Operation")
                        
        def make_gl_entries(self):
                tot_advance = 0.0
                
                if flt(self.total_amount) > 0:
                        from erpnext.accounts.general_ledger import make_gl_entries
                        gl_entries = []
                        currency = frappe.db.get_value(doctype="Customer", filters=self.party, fieldname=["default_currency"], as_dict=True)
                        
                        # Bank Entry
                        if flt(self.paid_amount) > 0:
                                rev_gl = frappe.db.get_value(doctype="Branch",filters=self.branch,fieldname="revenue_bank_account", as_dict=True)

                                if not rev_gl.revenue_bank_account:
                                        frappe.throw("Revenue Bank Account is not defined for the Branch.")
                                        
                                rev_gl_det = frappe.db.get_value(doctype="Account", filters=rev_gl.revenue_bank_account, fieldname=["account_type"], as_dict=True)
                                
                                gl_entries.append(
                                        self.get_gl_dict({"account": rev_gl.revenue_bank_account,
                                                         "debit": flt(self.paid_amount),
                                                         "debit_in_account_currency": flt(self.paid_amount),
                                                         "cost_center": self.cost_center,
                                                         "party_check": 0,
                                                         "account_type": rev_gl_det.account_type,
                                                         "is_advance": "No"
                                        }, currency.default_currency)
                                )

                        # Advance Entry
                        for adv in self.advances:
                                tot_advance += flt(adv.allocated_amount)

                        if flt(tot_advance) > 0:        
                                adv_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="project_advance_account", as_dict=True)

                                if not adv_gl.project_advance_account:
                                        frappe.throw("Project Advance Account is not defined in Projects Accounts Settings")
                                        
                                adv_gl_det = frappe.db.get_value(doctype="Account", filters=adv_gl.project_advance_account, fieldname=["account_type"], as_dict=True)
                                        
                                        
                                gl_entries.append(
                                        self.get_gl_dict({"account": adv_gl.project_advance_account,
                                                         "debit": flt(tot_advance),
                                                         "debit_in_account_currency": flt(tot_advance),
                                                         "cost_center": self.cost_center,
                                                         "party_check": 1 if adv_gl_det.account_type in ("Payable","Receivable") else 0,
                                                         "party_type": "Customer",
                                                         "party": self.party,
                                                         "account_type": adv_gl_det.account_type,
                                                         "is_advance": "No",
                                                         "reference_type": "Project Payment",
                                                         "reference_name": self.name,
                                                         "project": self.project
                                        }, currency.default_currency)
                                )

                        # Other Deductions
                        for ded in self.deductions:
                                if flt(ded.amount) > 0:
                                        if not ded.account:
                                                frappe.throw("Account cannot be blank under other deductions.")
                                                
                                        ded_gl_det = frappe.db.get_value(doctype="Account", filters=ded.account, fieldname=["account_type"], as_dict=True)
                                        gl_entries.append(
                                                self.get_gl_dict({"account": ded.account,
                                                                 "debit": flt(ded.amount),
                                                                 "debit_in_account_currency": flt(ded.amount),
                                                                 "cost_center": self.cost_center,
                                                                 "account_type": ded_gl_det.account_type,
                                                                 "is_advance": "No",
                                                                 "reference_type": "Project Payment",
                                                                 "reference_name": self.name,
                                                                 "project": self.project,
                                                                 "party_check": 1 if ded_gl_det.account_type in ("Payable","Receivable") else 0,
                                                                 "party_type": "Customer",
                                                                 "party": self.party
                                                }, currency.default_currency)
                                        )

                        # TDS Deductions
                        if flt(self.tds_amount) > 0:
                                if not self.tds_account:
                                        frappe.throw("TDS Account cannot be blank.")
                                        
                                tds_gl_det = frappe.db.get_value(doctype="Account", filters=self.tds_account, fieldname=["account_type"], as_dict=True)

                                gl_entries.append(
                                        self.get_gl_dict({"account": self.tds_account,
                                                        "debit": flt(self.tds_amount),
                                                        "debit_in_account_currency": flt(self.tds_amount),
                                                        "cost_center": self.cost_center,
                                                        "account_type": tds_gl_det.account_type,
                                                        "is_advance": "No",
                                                        "reference_type": "Project Payment",
                                                        "reference_name": self.name,
                                                        "project": self.project
                                        }, currency.default_currency)
                                )
                        # Receivable Account
                        if flt(self.total_amount) > 0:
                                rec_gl = frappe.db.get_value(doctype="Company",filters=self.company,fieldname="default_receivable_account", as_dict=True)
                                
                                if not rec_gl.default_receivable_account:
                                        frappe.throw("Default Receivables Account is not defined in Company Settings")

                                rec_gl_det = frappe.db.get_value(doctype="Account", filters=rec_gl.default_receivable_account, fieldname=["account_type"], as_dict=True)
                                        
                                gl_entries.append(
                                        self.get_gl_dict({"account": rec_gl.default_receivable_account,
                                                         "credit": flt(self.total_amount),
                                                         "credit_in_account_currency": flt(self.total_amount),
                                                         "cost_center": self.cost_center,
                                                         "party_check": 1,
                                                         "party_type": "Customer",
                                                         "party": self.party,
                                                         "account_type": rec_gl_det.account_type,
                                                         "is_advance": "No",
                                                         "reference_type": "Project Payment",
                                                         "reference_name": self.name,
                                                         "project": self.project
                                        }, currency.default_currency)
                                )
                                 
                        make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
                        
        def post_journal_entry(self):
                accounts    = []
                tot_advance = 0.0
                
                # Bank Entry
                if flt(self.paid_amount) > 0:
                        rev_gl = frappe.db.get_value(doctype="Branch",filters=self.branch,fieldname="revenue_bank_account", as_dict=True)
                        rev_gl_det = frappe.db.get_value(doctype="Account", filters=rev_gl.revenue_bank_account, fieldname=["account_type"], as_dict=True)
                        accounts.append({"account": rev_gl.revenue_bank_account,
                                         "debit_in_account_currency": flt(self.paid_amount),
                                         "cost_center": self.cost_center,
                                         "party_check": 0,
                                         "account_type": rev_gl_det.account_type,
                                         "is_advance": "No"
                        })

                # Advance Entry
                for adv in self.advances:
                        tot_advance += flt(adv.allocated_amount)

                if flt(tot_advance) > 0:        
                        adv_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="project_advance_account", as_dict=True)
                        adv_gl_det = frappe.db.get_value(doctype="Account", filters=adv_gl.project_advance_account, fieldname=["account_type"], as_dict=True)
                        accounts.append({"account": adv_gl.project_advance_account,
                                         "debit_in_account_currency": flt(tot_advance),
                                         "cost_center": self.cost_center,
                                         "party_check": 1,
                                         "party_type": "Customer",
                                         "party": self.party,
                                         "account_type": adv_gl_det.account_type,
                                         "is_advance": "No",
                                         "reference_type": "Project Payment",
                                         "reference_name": self.name,
                                         "project": self.project
                        })

                # Other Deductions
                for ded in self.deductions:
                        if flt(ded.amount) > 0 and ded.account:
                                ded_gl_det = frappe.db.get_value(doctype="Account", filters=ded.account, fieldname=["account_type"], as_dict=True)
                                accounts.append({"account": ded.account,
                                                 "debit_in_account_currency": flt(ded.amount),
                                                 "cost_center": self.cost_center,
                                                 "account_type": ded_gl_det.account_type,
                                                 "is_advance": "No",
                                                 "reference_type": "Project Payment",
                                                 "reference_name": self.name,
                                                 "project": self.project
                                })

                # TDS Deductions
                if flt(self.tds_amount) > 0 and self.tds_account:
                        tds_gl_det = frappe.db.get_value(doctype="Account", filters=self.tds_account, fieldname=["account_type"], as_dict=True)

                        accounts.append({"account": self.tds_account,
                                        "debit_in_account_currency": flt(self.tds_amount),
                                        "cost_center": self.cost_center,
                                        "account_type": tds_gl_det.account_type,
                                        "is_advance": "No",
                                        "reference_type": "Project Payment",
                                        "reference_name": self.name,
                                        "project": self.project
                                        })
                # Receivable Account
                if flt(self.total_amount) > 0:
                        rec_gl = frappe.db.get_value(doctype="Company",filters=self.company,fieldname="default_receivable_account", as_dict=True)
                        rec_gl_det = frappe.db.get_value(doctype="Account", filters=rec_gl.default_receivable_account, fieldname=["account_type"], as_dict=True)

                        accounts.append({"account": rec_gl.default_receivable_account,
                                         "credit_in_account_currency": flt(self.total_amount),
                                         "cost_center": self.cost_center,
                                         "party_check": 1,
                                         "party_type": "Customer",
                                         "party": self.party,
                                         "account_type": rec_gl_det.account_type,
                                         "is_advance": "No",
                                         "reference_type": "Project Payment",
                                         "reference_name": self.name,
                                         "project": self.project
                        })                         
                         
                        je = frappe.get_doc({
                                "doctype": "Journal Entry",
                                "voucher_type": "Bank Entry",
                                "naming_series": "Bank Receipt Voucher",
                                "title": "Project Payment - "+self.project,
                                "user_remark": "Project Payment - "+self.project,
                                "posting_date": nowdate(),
                                "company": self.company,
                                "total_amount_in_words": money_in_words(self.total_amount),
                                "accounts": accounts,
                                "branch": self.branch
                        })
                
                        je.submit()
                        
        def update_invoice_balance(self):
                for inv in self.references:
                        allocated_amount = 0.0
                        if flt(inv.allocated_amount) > 0:
                                result = frappe.db.sql("""
                                                select ifnull(total_balance_amount,0) as total_balance_amount
                                                from `tabProject Invoice`
                                                where name = %s
                                                and docstatus = 1
                                                """, (inv.reference_name), as_dict=1)[0]

                                if flt(result.total_balance_amount) < flt(inv.allocated_amount) and self.docstatus < 2:
                                        frappe.throw(_("Invoice#{0} : Allocated amount{1} cannot be more than Invoice Balance({2})").format(inv.reference_name, flt(inv.allocated_amount),flt(result.total_balance_amount)))
                                else:
                                        if self.docstatus < 2:
                                                allocated_amount = flt(inv.allocated_amount)
                                        else:
                                                allocated_amount = -1*flt(inv.allocated_amount)
                                                
                                        frappe.db.sql("""
                                                update `tabProject Invoice`
                                                set total_received_amount = ifnull(total_received_amount,0) + ifnull({0},0),
                                                        total_balance_amount = ifnull(total_balance_amount,0) - ifnull({1},0),
                                                        status = case
                                                                        when (ifnull(total_balance_amount,0) - ifnull({1},0)) > 0 then 'Unpaid'
                                                                        else 'Paid'
                                                                 end
                                                where name = '{2}'
                                                and docstatus = 1
                                        """.format(allocated_amount,allocated_amount,inv.reference_name))

        def update_advance_balance(self):
                for adv in self.advances:
                        allocated_amount = 0.0
                        if flt(adv.allocated_amount) > 0:
                                result = frappe.db.sql("""
                                                select ifnull(balance_amount,0) as balance_amount
                                                from `tabProject Advance`
                                                where name = %s
                                                and docstatus = 1
                                                """, (adv.reference_name), as_dict=1)[0]

                                if flt(result.balance_amount) < flt(adv.allocated_amount) and self.docstatus < 2:
                                        frappe.throw(_("Advance#{0} : Allocated amount{1} cannot be more than Advance Balance({2})").format(adv.reference_name, flt(adv.allocated_amount),flt(result.balance_amount)))
                                else:
                                        if self.docstatus < 2:
                                                allocated_amount = flt(adv.allocated_amount)
                                        else:
                                                allocated_amount = -1*flt(adv.allocated_amount)
                                        
                                        frappe.db.sql("""
                                                update `tabProject Advance`
                                                set adjustment_amount = ifnull(adjustment_amount,0) + ifnull({0},0),
                                                        balance_amount = ifnull(balance_amount,0) - ifnull({1},0)
                                                where name = '{2}'
                                                and docstatus = 1
                                        """.format(allocated_amount,allocated_amount,adv.reference_name))
                                        
        def update_boq_balance(self):
                for inv in self.references:
                        allocated_amount = 0.0
                        balance_amount   = 0.0
                        
                        result = frappe.db.sql("""
                                select boq, invoice_type
                                from `tabProject Invoice`
                                where name = '{0}'
                                and docstatus = 1
                        """.format(inv.reference_name),as_dict=1)[0]

                        if result.invoice_type == "MB Based Invoice":
                                mb_list = frappe.db.sql("""
                                        select boq, boq_type, entry_amount, price_adjustment_amount
                                        from `tabProject Invoice MB`
                                        where parent = '{0}'
                                        and is_selected = 1
                                        order by boq, parent
                                """.format(inv.reference_name), as_dict=1)

                                balance_amount = flt(inv.allocated_amount)
                                for mb in mb_list:
                                        allocated_amount = 0.0
                                        if flt(balance_amount) >= (flt(mb.entry_amount)+flt(mb.price_adjustment_amount)):
                                                allocated_amount = flt(mb.entry_amount)+flt(mb.price_adjustment_amount)
                                        else:
                                                allocated_amount = flt(balance_amount)

                                        balance_amount   = flt(balance_amount)-flt(allocated_amount) 
                                        allocated_amount = -1*flt(allocated_amount) if self.docstatus == 2 else flt(allocated_amount)
                                        frappe.db.sql("""
                                                update `tabBOQ`
                                                set received_amount = ifnull(received_amount,0) + ifnull({0},0),
                                                    balance_amount = ifnull(balance_amount,0) -  ifnull({0},0)
                                                where name = '{1}'
                                                and docstatus = 1
                                        """.format(allocated_amount, mb.boq))       
                        else:
                                if result.boq:
                                        allocated_amount = -1*flt(inv.allocated_amount) if self.docstatus == 2 else flt(inv.allocated_amount)
                                        
                                        frappe.db.sql("""
                                                update `tabBOQ`
                                                set received_amount = ifnull(received_amount,0) + ifnull({0},0),
                                                    balance_amount = ifnull(balance_amount,0) -  ifnull({0},0)
                                                where name = '{1}'
                                                and docstatus = 1
                                        """.format(allocated_amount, result.boq))
                
        def validate_invoice_balance(self):
                for inv in self.references:
                        if flt(inv.allocated_amount) > 0:
                                result = frappe.db.sql("""
                                                select ifnull(total_balance_amount,0) as total_balance_amount
                                                from `tabProject Invoice`
                                                where name = %s
                                                and docstatus = 1
                                                """, (inv.reference_name), as_dict=1)[0]

                                if flt(result.total_balance_amount) < flt(inv.allocated_amount):
                                        frappe.throw(_("Invoice#{0} : Allocated amount{1} cannot be more than Invoice Available Balance Amount({2})").format(inv.reference_name, flt(inv.allocated_amount),flt(result.total_balance_amount)))

        def validate_advance_balance(self):
                for adv in self.advances:
                        if flt(adv.allocated_amount) > 0:
                                result = frappe.db.sql("""
                                                select ifnull(balance_amount,0) as balance_amount
                                                from `tabProject Advance`
                                                where name = %s
                                                and docstatus = 1
                                                """, (adv.reference_name), as_dict=1)[0]

                                if flt(result.balance_amount) < flt(adv.allocated_amount):
                                        frappe.throw(_("Advance#{0} : Allocated amount{1} cannot be more than Advance Available Balance Amount({2})").format(adv.reference_name, flt(adv.allocated_amount),flt(result.total_balance_amount)))                                        
                
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

                if flt(self.total_amount) < 0:
                        frappe.throw(_("Total amount cannot be less than zero."),title="Invalid Data")
                        
                for adv in self.advances:
                        tot_adv_amount += adv.allocated_amount
                        if flt(adv.allocated_amount) > flt(adv.total_amount):
                                frappe.throw(_("Advance#{0} : Allocated amount cannot be more than available balance.").format(adv.reference_name))

                for inv in self.references:
                        tot_inv_amount += inv.allocated_amount
                        if flt(inv.allocated_amount) > flt(inv.total_amount):
                                frappe.throw(_("Invoice#{0} : Allocated amount cannot be more than available balance.").format(inv.reference_name))                        

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

        
	def get_series(self):
		fiscal_year = getdate(self.posting_date).year
		generate_receipt_no(self.doctype, self.name, self.branch, fiscal_year)

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
