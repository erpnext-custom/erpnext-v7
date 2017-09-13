# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate, nowdate
from erpnext.controllers.accounts_controller import AccountsController

class MechanicalPayment(AccountsController):
	def validate(self):
		self.check_amount()
		self.check_against_out()
		self.title = "Payment for " + str(self.ref_doc) + " (" + str(self.ref_no) + ")"

	def on_submit(self):
		self.make_gl_entry()
		self.update_ref_doc()

	def on_cancel(self):	
		self._gl_entry()
		self.update_ref_doc(cancel=1)

	def check_amount(self):
		if self.net_amount < 0:
			frappe.throw("Net Amount cannot be less than Zero")
		if self.tds_amount < 0:
			frappe.throw("TDS Amount cannot be less than Zero")
			
	def check_against_out(self):
		doc = frappe.get_doc(self.ref_doc, self.ref_no)
		if flt(doc.outstanding_amount < self.receivable_amount):
			frappe.throw("Receivable Amount cannot be greater than Outstanding Amount")

	def update_ref_doc(self, cancel=None):
		doc = frappe.get_doc(self.ref_doc, self.ref_no)
		if not cancel:
			doc.db_set("outstanding_amount", flt(doc.outstanding_amount) - flt(self.receivable_amount))
		else:
			doc.db_set("outstanding_amount", flt(doc.outstanding_amount) + flt(self.receivable_amount))

	def make_gl_entry(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		revenue_bank_account = frappe.db.get_value("Branch", self.branch, "revenue_bank_account")
		if not revenue_bank_account:
			frappe.throw("Setup Default Revenue Bank Account for your Branch")
		receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
		if not receivable_account:
			frappe.throw("Setup Default Receivable Account in Maintenance Setting")

		gl_entries = []
		gl_entries.append(
			self.get_gl_dict({"account": revenue_bank_account,
					 "debit": flt(self.net_amount),
					 "debit_in_account_currency": flt(self.net_amount),
					 "cost_center": self.cost_center,
					 "party_check": 1,
					 "reference_type": self.ref_doc,
					 "reference_name": self.ref_no,
					})
			)

		if self.tds_amount:
			gl_entries.append(
				self.get_gl_dict({"account": self.tds_account,
						 "debit": flt(self.tds_amount),
						 "debit_in_account_currency": flt(self.tds_amount),
						 "cost_center": self.cost_center,
						 "party_check": 1,
						 "reference_type": self.ref_doc,
						 "reference_name": self.ref_no,
						})
				)
		
		gl_entries.append(
			self.get_gl_dict({"account": receivable_account,
					 "credit": flt(self.receivable_amount),
					 "credit_in_account_currency": flt(self.receivable_amount),
					 "cost_center": self.cost_center,
					 "party_check": 1,
					 "party_type": "Customer",
					 "party": self.customer,
					 "reference_type": self.ref_doc,
					 "reference_name": self.ref_no,
					})
			)

		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
