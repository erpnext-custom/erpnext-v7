# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  SHIV		31/10/2017                            Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, get_url, nowdate
from frappe.model.document import Document

class CashJournalEntry(Document):
        def validate(self):
                self.refresh_defaults()
                self.get_employee()
                self.validate_defaults()

        def on_update(self):
                pass

        def on_submit(self):
                self.update_receipt()

        def on_cancel(self):
                self.update_receipt()

        def refresh_defaults(self):
                self.opening_balance = 0.0
                self.receipt_amount  = 0.0
                self.purchase_amount = 0.0
                self.closing_balance = 0.0
                        
                if self.entry_type == "Receipt":
                        self.receipt_amount      = flt(self.amount)
                        self.reference_no        = ""
                        self.cash_journal_detail = []
                elif self.entry_type == "Purchase":
                        self.amount          = 0.0
                        self.opening_balance = get_opening_balance(self.reference_no)
                        
                        for item in self.cash_journal_detail:
                                item.amount           = flt(item.quantity)*flt(item.rate)
                                self.purchase_amount += (flt(item.quantity)*flt(item.rate))

                if self.entry_type == 'Purchase' and self.reference_no and not self.project:
                        self.project = frappe.db.get_value("Cash Journal Entry", self.reference_no, "project")

                if self.project:
                        base_project      = frappe.get_doc("Project", self.project)
                        self.project_name = base_project.project_name
                        self.branch       = base_project.branch
                        self.cost_center  = base_project.cost_center

                        if base_project.status in ('Completed','Cancelled'):
                                frappe.throw(_("Operation not permitted on already {0} Project.").format(base_project.status),title="Cash Journal: Invalid Operation")

                if not self.cost_center:
                        emp = frappe.db.sql("""
                                select
                                        cost_center,
                                        branch
                                from `tabEmployee`
                                where user_id = '{0}'
                                order by creation desc
                                limit 1
                                """.format(frappe.session.user), as_dict=1)[0]

                        if emp:
                                self.branch      = emp.branch
                                self.cost_center = emp.cost_center
                        else:
                                frappe.throw(_("Cost Center not defined for the user."), title="Missing Value")
                        
                self.closing_balance = flt(self.opening_balance) + flt(self.receipt_amount) - flt(self.purchase_amount)

        def get_employee(self):
                emp = frappe.db.sql("""
                        select
                                name,
                                department,
                                division,
                                section,
                                branch,
                                cost_center,
                                case
                                        when status = 'Active' then 1
                                        when status is null then 2
                                        else 3
                                end as sort_order
                        from `tabEmployee`
                        where user_id = '{0}'
                        order by sort_order, creation
                        limit 1
                """.format(frappe.session.user), as_dict=1)

                if emp:
                        self.employee             = emp[0].name
                        self.department           = emp[0].department
                        self.division             = emp[0].division
                        self.section              = emp[0].section
                        self.employee_branch      = emp[0].branch
                        self.employee_cost_center = emp[0].cost_center
                
        def validate_defaults(self):
                if self.entry_type == 'Receipt' and flt(self.receipt_amount,0) < 0:
                        frappe.throw(_("Receipt Amount cannot be a negative value."), title='Invalid Value')

                if self.entry_type == 'Purchase' and flt(self.purchase_amount,0) < 0:
                        frappe.throw(_("Purchase Amount cannot be a negative value."), title='Invalid Value')

                if flt(self.purchase_amount) > flt(self.opening_balance):
                        frappe.throw(_("Purchase Amount(Nu.{0}) cannot exceed Available Balance/Opening Balance(Nu.{1}).").format(flt(self.purchase_amount),flt(self.opening_balance)), title='Insufficient Balance')

                for item in self.cash_journal_detail:
                        if flt(item.amount) < 0:
                                frappe.throw(_("Row# {0}: Amount cannot be a negative value.").format(item.idx), title='Invalid Value')

        def update_receipt(self):
                #Update Receipt
                if self.entry_type == 'Purchase' and self.reference_no:
                        purchase_amount = flt(self.purchase_amount)*(1 if self.docstatus < 2 else -1)
                        base_receipt = frappe.get_doc("Cash Journal Entry", self.reference_no)

                        if flt(purchase_amount) > 0.0 and flt(purchase_amount) > flt(base_receipt.closing_balance):
                                frappe.throw(_("Purchase Amount(Nu.{0}) cannot exceed Available Balance(Nu.{1})").format(flt(self.purchase_amount), flt(base_receipt.closing_balance)), title='Insufficient Balance')
                        
                        base_receipt.db_set("purchase_amount", flt(base_receipt.purchase_amount)+flt(purchase_amount))
                        base_receipt.db_set("closing_balance", flt(base_receipt.closing_balance)-flt(purchase_amount))

                #Update Project
                if self.project:
                        base_project = frappe.get_doc("Project", self.project)
                        tot_receipt_amt  = 0.0
                        tot_purchase_amt = 0.0

                        tot_receipt_amt  = flt(base_project.imprest_received)+(flt(self.receipt_amount)*(1 if self.docstatus < 2 else -1))
                        tot_purchase_amt = flt(base_project.imprest_purchased)+(flt(self.purchase_amount)*(1 if self.docstatus < 2 else -1))
                        
                        if flt(tot_receipt_amt) > flt(base_project.imprest_limit):
                                frappe.throw(_("Receipt Amount exceeding Imprest Limit by Nu.{0}".format(flt(tot_receipt_amt)-flt(base_project.imprest_limit))), title="Imprest Limit Reached")

                        base_project.db_set("imprest_received",flt(tot_receipt_amt))
                        base_project.db_set("imprest_purchased",flt(tot_purchase_amt))
                        base_project.db_set("imprest_receivable",flt(base_project.imprest_limit)-flt(tot_receipt_amt))

@frappe.whitelist()
def get_opening_balance(reference_no = None):
        result = frappe.db.sql("""
                        select ifnull(closing_balance,0) as opening_balance
                        from `tabCash Journal Entry`
                        where name       = '{0}'
                        and   docstatus  = 1
                        and   entry_type = 'Receipt' 
        """.format(reference_no))

        if result:
                return result[0][0]
        else:
                return 0.0
