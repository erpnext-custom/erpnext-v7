# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import check_budget_available
import json
from frappe import _
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words


class PolAdvance(AccountsController):
    def validate(self):
        self.set_branch_cost_center()
        self.validate_cheque_info()
        if self.workflow_state == "Waiting For Payment"	:
            if "Accounts Manager" not in frappe.get_roles(frappe.session.user):
                    self.approved_by = frappe.session.user
        self.od_adjustement()

    def set_branch_cost_center(self):
        self.fuelbook_branch = frappe.db.get_value('Fuelbook',self.fuelbook,['branch'])
        self.cost_center = frappe.db.get_value('Branch',self.fuelbook_branch,['cost_center'])
        self.company = frappe.defaults.get_defaults().company
        self.branch = self.fuelbook_branch

    def before_cancel(self):
        if self.journal_entry:
            for t in frappe.get_all("Journal Entry", ["name"], {"name": self.journal_entry, "docstatus": ("<",2)}):
                frappe.throw(_('Journal Entry  <a href="#Form/Journal Entry/{0}">{0}</a> for this transaction needs to be cancelled first').format(self.journal_entry),title='Not permitted')

    def on_submit(self):
        advance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "pol_advance_account")
        check_budget_available(self.cost_center,advance_account,self.entry_date,self.amount,self.business_activity)
        self.update_od_balance()
        self.post_journal_entry()

    def on_cancel(self):
        self.cancel_budget_entry()
        self.update_od_balance()

    def update_od_balance(self):
        # for d in self.items:
        #     doc = frappe.get_doc('Pol Advance',d.reference)
        #     if self.docstatus == 2 :
        #         self.adjusted_amount = flt(self.adjusted_amount) - flt(doc.od_amount)
        #         self.balance_amount = flt(self.balance_amount) + flt(doc.od_amount)
        #         doc.od_adjusted_amount = 0 
        #         doc.od_outstanding_amount = doc.od_amount
        #         doc.save(ignore_permissions=True)
        #     elif self.docstatus == 1:
        #         self.adjusted_amount += flt(doc.od_amount)
        #         self.balance_amount = flt(self.amount) - flt(self.adjusted_amount)
        #         doc.od_adjusted_amount = doc.od_outstanding_amount 
        #         doc.od_outstanding_amount = 0
        #         doc.save(ignore_permissions=True)
        #         self.save()

        for d in self.items:
            doc = frappe.get_doc('Pol Advance',d.reference)
            if self.docstatus == 2:
                if flt(self.adjusted_amount) - flt(doc.od_amount) < 0:
                    self.adjusted_amount = 0
                    self.balance_amount = flt(self.amount)
                else:
                    self.adjusted_amount = flt(self.adjusted_amount) - flt(doc.od_amount)
                    self.balance_amount = flt(self.balance_amount) + flt(doc.od_amount)
                doc.od_adjusted_amount = 0 
                doc.od_outstanding_amount = doc.od_amount
                doc.save(ignore_permissions=True)
            elif self.docstatus == 1:
                if flt(self.adjusted_amount) == flt(self.amount):
                    self.od_amount += doc.od_amount
                    self.od_outstanding_amount += doc.od_amount
                elif flt(self.adjusted_amount) + flt(doc.od_amount) > flt(self.amount):
                    excess_amount = flt(self.adjusted_amount) + flt(doc.od_amount) - flt(self.amount)
                    self.od_amount = flt(excess_amount)
                    self.od_outstanding_amount = flt(excess_amount)
                    self.adjusted_amount = flt(self.amount)
                    self.balance_amount = flt(self.amount) - flt(self.adjusted_amount)
                else:
                    self.adjusted_amount += flt(doc.od_amount)
                    self.balance_amount = flt(self.amount) - flt(self.adjusted_amount)
                doc.od_adjusted_amount = doc.od_outstanding_amount 
                doc.od_outstanding_amount = 0
                doc.save(ignore_permissions=True)
                self.save()
    def od_adjustement(self):
        data = frappe.db.sql('''
            SELECT
                name as reference, od_amount,
                od_outstanding_amount
            FROM `tabPol Advance`
            WHERE od_outstanding_amount > 0
            and docstatus = 1
            and equipment = '{}'
        '''.format(self.equipment),as_dict=True)
        
        if data :
            self.set('items',[])
            for d in data:
                row = self.append('items',{})
                row.update(d)

    def validate_cheque_info(self):
        if self.cheque_date and not self.cheque_no:
            msgprint(_("Cheque No is mandatory if you entered Cheque Date"), raise_exception=1)
  
    def cancel_budget_entry(self):
        frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name) 
   
    def post_journal_entry(self):

        if not self.amount:
            frappe.throw(_("Amount should be greater than zero"))
        self.posting_date = self.entry_date
        ba = self.business_activity

        # payable_account = frappe.db.get_value("Company", self.company, "default_payable_account")
        credit_account = self.expense_account
        advance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "pol_advance_account")
            
        if not credit_account:
            frappe.throw("Expense Account is mandatory")
        if not advance_account:
            frappe.throw("Setup POL Advance Account in Maintenance Accounts Settings")

        account_type = frappe.db.get_value("Account", advance_account, "account_type")
        party_type = ''
        party = ''
        if account_type == "Payable":
            party_type = self.party_type
            party = self.supplier

        r = []
        if self.cheque_no:
            if self.cheque_date:
                r.append(_('Reference #{0} dated {1}').format(self.cheque_no, formatdate(self.cheque_date)))
            else:
                msgprint(_("Please enter Cheque Date date"), raise_exception=frappe.MandatoryError)
        if self.user_remark:
            r.append(_("Note: {0}").format(self.user_remark))

        remarks = ("").join(r) #User Remarks is not mandatory

        # Posting Journal Entry
        je = frappe.new_doc("Journal Entry")

        je.update({
            "doctype": "Journal Entry",
            "voucher_type": "Bank Entry",
            "naming_series": "Bank Receipt Voucher" if self.payment_type == "Receive" else "Bank Payment Voucher",
            "title": "POL Advance - " + self.equipment,
            "user_remark": remarks if remarks else "Note: " + "POL Advance - " + self.equipment,
            "posting_date": self.posting_date,
            "company": self.company,
            "total_amount_in_words": money_in_words(self.amount),
            "branch": self.fuelbook_branch
        })

        je.append("accounts",{
            "account": credit_account,
            "credit_in_account_currency": self.amount,
            "cost_center": self.cost_center,
            "reference_type": "Pol Advance",
            "reference_name": self.name,
            "business_activity": ba
        })


        je.append("accounts",{
            "account": advance_account,
            "debit_in_account_currency": self.amount,
            "cost_center": self.cost_center,
            "party_check": 0,
            "party_type": party_type,
            "party": party,
            "business_activity": ba
        })

        je.insert()
        #Set a reference to the claim journal entry
        self.db_set("journal_entry",je.name)
        frappe.msgprint(_('Journal Entry <a href="#Form/Journal Entry/{0}">{0}</a> posted to accounts').format(je.name))

# Added by Sonam Chophel to update the payment status on august 31/08/2021
# @frappe.whitelist()
# def get_payment_entry(doc_name=None, journal_entry=None):
#     """ see if there exist a journal entry submitted for the pol advance """
#     status = frappe.db.get_value("Journal Entry", journal_entry, "docstatus")
#     if status == 1:
#         frappe.db.set_value("Pol Advance", doc_name, "payment_status", "Paid")
#         return ("Paid")
#     elif status == 0:
#         frappe.db.set_value("Pol Advance", doc_name, 'payment_status', "Waiting for Payment")
#         return ("Waiting for Payment")
#     else:
#         frappe.db.set_value("Pol Advance", doc_name, 'payment_status', "Cancelled")
#         return ("Cancelled")
# -------- End of new code ----------