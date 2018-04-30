# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.accounts.doctype.imprest_receipt.imprest_receipt import get_opening_balance, update_dependencies
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_gl_entries

class ImprestRecoup(AccountsController):
	def validate(self):
                self.update_defaults()
                self.update_amounts()
                self.validate_amounts()

        def on_submit(self):
                for t in frappe.get_all("Imprest Recoup", ["name"], {"branch": self.branch, "entry_date":("<",self.entry_date),"docstatus":0}):
                        msg = '<b>Reference# : <a href="#Form/Imprest Recoup/{0}">{0}</a></b>'.format(t.name)
                        frappe.throw(_("Found unclosed entries. Previous entries needs to be either closed or cancelled in order to determine opening balance for the current transaction.<br>{0}").format(msg),title="Invalid Operation")
                self.post_receipt_entry()
                self.post_gl_entry()
        
        def on_cancel(self):
                for t in frappe.get_all("Imprest Receipt", ["name"], {"name": self.imprest_receipt, "docstatus":1}):
                        msg = '<b>Reference# : <a href="#Form/Imprest Receipt/{0}">{0}</a></b>'.format(t.name)
                        frappe.throw(_("You need to cancel dependent Imprest Receipt entry first.<br>{0}").format(msg),title="Invalid Operation")
                        
                self.post_gl_entry()
                update_dependencies(self.branch, self.entry_date)
                
        def update_defaults(self):
                # Update entry_date
                if not self.entry_date:
                        self.entry_date = now_datetime()

                if self.docstatus == 0 and self.workflow_state == "Recouped":
                        self.workflow_state = "Waiting Recoupment"

                # Update items
                self.purchase_amount = 0.0
                for i in self.items:
                        i.amount = flt(i.quantity)*flt(i.rate)
                        if flt(i.quantity) <= 0.0:
                                frappe.throw(_("Row#{0} : Please input valid data for quantity.").format(i.idx),title="Invalid Quantity")
                        elif flt(i.rate) <= 0.0:
                                frappe.throw(_("Row#{0} : Please input valid data for rate.").format(i.idx),title="Invalid Rate")
                        elif flt(i.amount) < 0.0:
                                frappe.throw(_("Row#{0} : Amount cannot be a negative value.").format(i.idx),title="Invalid Amount")
                        

                        self.purchase_amount += flt(i.amount)
                
        def update_amounts(self):
                opening_balance = get_opening_balance(self.branch, self.name, self.entry_date)
                if flt(opening_balance) != flt(self.opening_balance):
                        #frappe.msgprint(_("Opening balance has been changed from Nu.{0}/- to Nu.{1}/-").format(flt(self.opening_balance),flt(opening_balance)),title="Change in values")
                        self.opening_balance = flt(opening_balance)

                self.closing_balance = flt(self.opening_balance)+flt(self.receipt_amount)-flt(self.purchase_amount)

        def validate_amounts(self):
                if flt(self.opening_balance) <= 0:
                        frappe.throw("Insufficient Opening balance...",title="Insufficient Balance")
                elif flt(self.purchase_amount) < 0:
                        frappe.throw("Purchase amount cannot be a negative value.",title="Invalid Data")
                elif not self.purchase_amount:
                        frappe.throw("Purchase amount cannot be empty.",title="Invalid Data")
                        
                # Validate against imprest limit set under branch
                imprest_limit = frappe.db.get_value("Branch", self.branch, "imprest_limit")

                if not imprest_limit:
                        frappe.throw("Please set imprest limit for the branch.", title="Insufficient Balance")
                else:
                        if flt(self.closing_balance) > flt(imprest_limit):
                                frappe.throw(_("Closing balance cannot exceed imprest limit Nu.{0}/-.").format(flt(imprest_limit)),title="Invalid Data")

        def post_receipt_entry(self):
                if self.purchase_amount:
                        doc = frappe.new_doc("Imprest Receipt")
                        doc.update({
                                "doctype": "Imprest Receipt",
                                "company": self.company,
                                "branch": self.branch,
                                "title": "Recoupment for "+str(self.name),
                                "entry_date": now_datetime(),
                                "amount": flt(self.purchase_amount),
                                "revenue_bank_account": self.revenue_bank_account,
                                "pay_to_recd_from": self.pay_to_recd_from,
                                "select_cheque_lot": self.select_cheque_lot,
                                "cheque_no": self.cheque_no,
                                "cheque_date": self.cheque_date,
                                "imprest_recoup": self.name,
                                "workflow_state": "Approved"
                        })
                        doc.save(ignore_permissions = True)
                        doc.submit()
                        #self.imprest_receipt = doc.name
                        self.db_set("imprest_receipt", doc.name)
                else:
                        frappe.throw(_("Purchase amount cannot be empty."),title="Invalid Data")
        
        def post_gl_entry(self):
                gl_entries      = []
                entries         = {}
                accounts        = []
                total_amount    = 0.0
                rev_gl = frappe.db.get_value(doctype="Branch",filters=self.branch,fieldname="revenue_bank_account", as_dict=True)
                self.posting_date = nowdate()

                if not rev_gl.revenue_bank_account:
                        frappe.throw(_("Bank Account GL is not defined in Branch '{0}'.").format(self.branch),title="Data Not found")

                for i in self.items:
                        total_amount += flt(i.amount)
                        if not i.budget_account:
                                frappe.throw(_("Row#{0} : Please select proper budget account.").format(i.idx),title="Missing Data")
                                
                        if entries.has_key(i.budget_account):
                                entries[i.budget_account]['amount'] += flt(i.amount)
                        else:
                                entries[i.budget_account]  = {"type": "debit", "amount": flt(i.amount)}

                entries[rev_gl.revenue_bank_account] = {"type": "credit", "amount": flt(total_amount)}

                for gl in entries:
                        gl_entries.append(
                                self.get_gl_dict({
                                       "account": gl,
                                       "debit" if entries[gl]["type"] == "debit" else "credit": entries[gl]["amount"],
                                       "debit_in_account_currency" if entries[gl]["type"] == "debit" else "credit_in_account_currency": entries[gl]["amount"],
                                       "voucher_no": self.name,
                                       "voucher_type": self.doctype,
                                       "cost_center": self.cost_center,
                                       "company": self.company,
                                       "remarks": self.branch
                                })
                        )
                
                make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
        
        def post_journal_entry(self):
                entries         = {}
                accounts        = []
                total_amount    = 0.0
                
                # Fetching GLs
                rev_gl = frappe.db.get_value(doctype="Branch",filters=self.branch,fieldname="revenue_bank_account", as_dict=True)
                
                if not rev_gl.revenue_bank_account:
                        frappe.throw(_("Bank Account GL is not defined in Branch '{0}'.").format(self.branch),title="Data Not found")

                for i in self.items:
                        total_amount += flt(i.amount)
                        if not i.budget_account:
                                frappe.throw(_("Row#{0} : Please select proper budget account.").format(i.idx),title="Missing Data")
                                
                        if entries.has_key(i.budget_account):
                                entries[i.budget_account]['amount'] += flt(i.amount)
                        else:
                                entries[i.budget_account]  = {"type": "debit", "amount": flt(i.amount)}

                entries[rev_gl.revenue_bank_account] = {"type": "credit", "amount": flt(total_amount)}
                
                for gl in entries:
                        gl_det = frappe.db.get_value(doctype="Account", filters=gl, fieldname=["account_type","is_an_advance_account"], as_dict=True)                        
                        accounts.append({"account": gl,
                                 "debit_in_account_currency" if entries[gl]["type"]=="debit" else "credit_in_account_currency": flt(entries[gl]["amount"]),
                                 "cost_center": self.cost_center,
                                 "party_check": 0,
                                 "account_type": gl_det.account_type,
                                 "is_advance": "Yes" if gl_det.is_an_advance_account == 1 else None
                        })

                je = frappe.new_doc("Journal Entry")
                
                je.update({
                        "doctype": "Journal Entry",
                        "voucher_type": "Bank Entry",
                        "naming_series": "Bank Payment Voucher",
                        "title": "Imprest Recoupment ("+str(self.name)+")",
                        "user_remark": "Imprest Recoupment ("+str(self.name)+")",
                        "posting_date": nowdate(),
                        "company": self.company,
                        "total_amount_in_words": money_in_words(total_amount),
                        "accounts": accounts,
                        "branch": self.branch,
                        "imprest_recoup": self.name
                })
                je.save(ignore_permissions = True)
