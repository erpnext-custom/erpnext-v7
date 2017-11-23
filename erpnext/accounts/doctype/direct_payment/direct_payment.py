# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint

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
		je.branch = self.branch

		account_type = frappe.db.get_value("Account", self.budget_account, "account_type")
		if str(account_type) == "Payable":
			je.append("accounts", {
					"account": self.budget_account,
					"reference_type": "Direct Payment",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"party_type": "Supplier",
					"party": self.supplier,
					"debit_in_account_currency": flt(self.amount),
					"debit": flt(self.amount),
				})
		else:
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

		je.insert()

		self.db_set("journal_entry", je.name)

	def on_cancel(self):
		jv = frappe.db.sql("select name, docstatus from `tabJournal Entry` where name = %s and docstatus != 2", self.journal_entry)
		if jv:
			frappe.throw("Can not cancel PBVA without canceling the corresponding journal entry " + str(self.journal_entry))
		else:
			self.db_set("journal_entry", "")


@frappe.whitelist()
def get_tds_account(percent):
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
			frappe.throw("Set TDS Accounts in Accounts Settings and try again")		

		return frappe.db.get_single_value("Accounts Settings", field)
	
