# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, cstr, flt, fmt_money, formatdate, nowdate
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import generate_receipt_no, check_future_date
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba

class MechanicalPayment(AccountsController):
	def validate(self):
		check_future_date(self.posting_date)
		self.check_amount()
		self.check_against_out()
		self.title = "Payment for " + str(self.ref_doc) + " (" + str(self.ref_no) + ")"

	def on_submit(self):
		self.make_gl_entry()
		self.update_ref_doc()

	def on_cancel(self):	
		self.make_gl_entry()
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

	def get_series(self):
		fiscal_year = getdate(self.posting_date).year
		generate_receipt_no(self.doctype, self.name, self.branch, fiscal_year)

	def make_gl_entry(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
		if not receivable_account:
			frappe.throw("Setup Default Receivable Account in Maintenance Setting")

		ba = get_default_ba()

		gl_entries = []
		gl_entries.append(
			self.get_gl_dict({"account": self.income_account,
					 "debit": flt(self.net_amount),
					 "debit_in_account_currency": flt(self.net_amount),
					 "cost_center": self.cost_center,
					 "party_check": 1,
					 "reference_type": self.ref_doc,
					 "reference_name": self.ref_no,
					 "business_activity": ba,
					 "remarks": self.remarks
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
						 "business_activity": ba,
						 "remarks": self.remarks
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
					 "business_activity": ba,
					 "remarks": self.remarks
					})
			)

		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
