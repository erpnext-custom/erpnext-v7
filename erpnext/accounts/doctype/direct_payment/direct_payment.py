# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.accounts.general_ledger import make_gl_entries
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import check_future_date

class DirectPayment(AccountsController):
    def validate(self):
        check_future_date(self.posting_date)
        self.validate_data()
        self.clearance_date = None
        self.validate_tds_account()

    def on_submit(self):
        self.post_gl_entry()
        self.consume_budget()
        
    def before_cancel(self):
        pass

    def on_cancel(self):
        if self.clearance_date:
            frappe.throw("Already done bank reconciliation.")
        self.post_gl_entry()
        self.cancel_budget_entry()

    def validate_data(self):
        tds_amt = gross_amt = net_amt = taxable_amt = deduction_amt = 0.00
        if self.deduct:
            for d in self.deduct:
                deduction_amt += flt(d.amount)
            self.deduction_amount = flt(deduction_amt)
        else:
            self.deduction_amount = 0.00
        
        for a in self.item:
            if self.payment_type == "Receive":
                inter_company = frappe.db.get_value(
                    "Customer", self.party, "inter_company")
                if inter_company == 0:
                    frappe.throw(
                        _("Selected Customer {0} is not inter company ".format(self.party)))

            if self.payment_type == "Payment" and a.party_type == "Customer":
                frappe.throw(
                    _("Party Type should be Supplier in Child table when Payment Type is Payment"))
            elif self.payment_type == "Receive" and a.party_type == "Supplier":
                frappe.throw(
                    _("Party Type should be Customer in Child Table when Payment Type is Receive"))
            if a.tds_applicable:
                if not self.tds_percent:
                    frappe.throw("Select TDS Percent for tds deduction")
                if self.tds_percent and cint(self.tds_percent) > 0:
                    a.tds_amount = flt(a.taxable_amount) * \
                        flt(self.tds_percent) / 100
            else:
                a.tds_amount = 0.00

            a.net_amount = flt(a.amount) - flt(a.tds_amount)
            tds_amt += flt(a.tds_amount)
            gross_amt += flt(a.amount)
            net_amt += flt(a.net_amount)
            taxable_amt += flt(a.taxable_amount)

        self.tds_amount = tds_amt
        self.gross_amount = gross_amt
        self.amount = gross_amt
        self.net_amount = flt(net_amt) - flt(deduction_amt)
        self.taxable_amount = taxable_amt

    ##
    # Update the Committedd Budget for checking budget availability
    ##
    def consume_budget(self):
        if self.payment_type == "Payment":
            for a in self.item:
                bud_obj = frappe.get_doc({
                    "doctype": "Committed Budget",
                    "account": a.account,
                    "cost_center": self.cost_center,
                    "po_no": self.name,
                    "po_date": self.posting_date,
                    "amount": a.amount,
                    "poi_name": self.name,
                    "date": frappe.utils.nowdate(), 
                    "business_activity": self.business_activity
                })
                bud_obj.flags.ignore_permissions = 1
                bud_obj.submit()

                consume = frappe.get_doc({
                    "doctype": "Consumed Budget",
                    "account": a.account,
                    "cost_center": self.cost_center,
                    "po_no": self.name,
                    "po_date": self.posting_date,
                    "amount": a.amount,
                    "pii_name": self.name,
                    "com_ref": bud_obj.name,
                    "business_activity": self.business_activity,
                    "date": frappe.utils.nowdate()})
                consume.flags.ignore_permissions = 1
                consume.submit()
    ##
    # Cancel budget check entry
    ##
    def cancel_budget_entry(self):
        frappe.db.sql(
            "delete from `tabCommitted Budget` where po_no = %s", self.name)
        frappe.db.sql(
            "delete from `tabConsumed Budget` where po_no = %s", self.name)
        
    def add_bank_gl_entries(self, gl_entries):
        party = party_type = None
        if self.payment_type == "Receive":
            account_type = frappe.db.get_value("Account", self.debit_account, "account_type") or ""
            if account_type in ["Receivable", "Payable"]:
                party = a.party
                party_type = a.party_type
            gl_entries.append(
                self.get_gl_dict({
                    "account": self.debit_account,
                    "debit": self.net_amount,
                    "debit_in_account_currency": self.net_amount,
                    "voucher_no": self.name,
                    "voucher_type": self.doctype,
                    "cost_center": self.cost_center,
                    "party_type": party_type,
                    "party": party,
                    "company": self.company,
                    "remarks": self.remarks,
                    "business_activity": self.business_activity,
                    })
                )
        else:
            account_type = frappe.db.get_value("Account", self.credit_account, "account_type") or ""
            if account_type in ["Receivable", "Payable"]:
                party = self.party
                party_type = self.party_type
            gl_entries.append(
                self.get_gl_dict({
                    "account": self.credit_account,
                    "credit": self.net_amount,
                    "credit_in_account_currency": self.net_amount,
                    "voucher_no": self.name,
                    "voucher_type": self.doctype,
                    "cost_center": self.cost_center,
                    "party_type": party_type,
                    "party": party,
                    "company": self.company,
                    "remarks": self.remarks,
                    "business_activity": self.business_activity,
                    })
                )
    
    def add_party_gl_entries(self, gl_entries):
        for a in self.item:
            party = party_type = None
            account_type = frappe.db.get_value("Account", a.account, "account_type") or ""
            if account_type in ["Receivable", "Payable"]:
                party = a.party
                party_type = a.party_type
            if self.payment_type == "Receive":
                gl_entries.append(
                    self.get_gl_dict({
                        "account": a.account,
                        "credit": a.amount,
                        "credit_in_account_currency": a.amount,
                        "voucher_no": self.name,
                        "voucher_type": self.doctype,
                        "cost_center": self.cost_center,
                        'party': party,
                        'party_type': party_type,						
                        "company": self.company,
                        "remarks": self.remarks,
                        "business_activity": self.business_activity,
                        })
                    )
            else:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": a.account,
                        "debit": a.amount,
                        "debit_in_account_currency": a.amount,
                        "voucher_no": self.name,
                        "voucher_type": self.doctype,
                        "cost_center": self.cost_center,
                        'party': party,
                        'party_type': party_type,						
                        "company": self.company,
                        "remarks": self.remarks,
                        "business_activity": self.business_activity,
                        })
                    )
        if self.deduct:
            for a in self.deduct:
                debit_account_type = frappe.db.get_value("Account", a.account, "account_type") or ""
                party = party_type = None
                if debit_account_type in ["Receivable", "Payable"]:
                    party = a.party
                    party_type = a.party_type
                gl_entries.append(
                        self.get_gl_dict({
                            "account": a.account,
                            "credit": a.amount,
                            "credit_in_account_currency": a.amount,
                            "voucher_no": self.name,
                            "voucher_type": self.doctype,
                            "cost_center": self.cost_center,
                            "party": party,
                            "party_type": party_type,
                            "company": self.company,
                            "remarks": self.remarks,
                            "business_activity": self.business_activity,
                            })
                        )
               
    def add_tds_gl_entries(self, gl_entries):
        if flt(self.tds_amount) > 0:
            if self.payment_type == "Received":
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.tds_account,
                        "debit": self.tds_amount,
                        "debit_in_account_currency": self.tds_amount,
                        "voucher_no": self.name,
                        "voucher_type": self.doctype,
                        "cost_center": self.cost_center,
                        "company": self.company,
                        "remarks": self.remarks,
                        "business_activity": self.business_activity,
                        })
                    )
            else:
                gl_entries.append(
                    self.get_gl_dict({
                        "account": self.tds_account,
                        "credit": self.tds_amount,
                        "credit_in_account_currency": self.tds_amount,
                        "voucher_no": self.name,
                        "voucher_type": self.doctype,
                        "cost_center": self.cost_center,
                        "company": self.company,
                        "remarks": self.remarks,
                        "business_activity": self.business_activity,
                        })
                    )
                
    def post_gl_entry(self):
        gl_entries = []
        self.add_party_gl_entries(gl_entries)
        self.add_bank_gl_entries(gl_entries)
        self.add_tds_gl_entries(gl_entries)
        make_gl_entries(gl_entries, cancel=(self.docstatus == 2),
                        update_outstanding="No", merge_entries=False)
    
    def validate_tds_account(self):
        if not self.tds_account and self.tds_percent:
            self.tds_account = get_tds_account(self.tds_percent, payment_type ="Payment")
            
@frappe.whitelist()
def get_tds_account(percent, payment_type):
    if payment_type == "Payment":
        if percent:
            if cint(percent) == 2:
                field = "tds_2_account"
            elif cint(percent) == 3:
                field = "tds_3_account"
            elif cint(percent) == 5:
                field = "tds_5_account"
            elif cint(percent) == 10:
                field = "tds_10_account"
            else:
                frappe.throw(
                    "Set TDS Accounts in Accounts Settings and try again")
            return frappe.db.get_single_value("Accounts Settings", field)

    elif payment_type == "Receive":
        if percent:
            field = "tds_deducted"
            return frappe.db.get_single_value("Accounts Settings", field)