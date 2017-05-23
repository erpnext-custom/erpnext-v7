# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class DirectPayment(Document):
	def validate(self):
		pass

	def on_submit(self):
		self.post_journal_entry()

	def post_journal_entry(self):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Direct Payment (" + self.supplier + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Direct payment against : ' + self.name;
		je.posting_date = self.posting_date

		je.append("accounts", {
				"account": self.budget_account,
				"reference_type": "Direct Payment",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.amount),
				"debit": flt(self.amount),
			})
		
		je.append("accounts", {
				"account": self.credit_account,
				"reference_type": "Direct Payment",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.balance_amount),
				"credit": flt(self.balance_amount),
			})
		
		je.append("accounts", {
				"account": self.tds_account,
				"reference_type": "Direct Payment",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.tds_amount),
				"credit": flt(self.tds_amount),
			})

		je.append("accounts", {
				"account": "Sundry Creditors - Domestic - SMCL",
				"reference_type": "Direct Payment",
				"reference_name": self.name,
				"party_type": "Supplier",
				"party": self.supplier,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.amount),
				"credit": flt(self.amount),
			})

		je.append("accounts", {
				"account": "Sundry Creditors - Domestic - SMCL",
				"reference_type": "Direct Payment",
				"reference_name": self.name,
				"party_type": "Supplier",
				"party": self.supplier,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.amount),
				"debit": flt(self.amount),
			})
		je.insert()

		self.db_set("journal_entry", je.name)

	def on_cancel(self):
		jv = frappe.db.sql("select name, docstatus from `tabJournal Entry` where name = %s and docstatus = 1", self.journal_entry)
		if jv:
			frappe.throw("Can not cancel PBVA without canceling the corresponding journal entry " + str(self.journal_entry))
		else:
			self.db_set("journal_entry", "")


