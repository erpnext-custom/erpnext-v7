# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_utils import check_budget_available
from frappe import _
from frappe.utils import flt, cint, nowdate, getdate, formatdate, money_in_words

class Reimbursement(Document):
	def before_cancel(self):
		if self.journal_entry:
			for t in frappe.get_all("Journal Entry", ["name"], {"name": self.journal_entry, "docstatus": ("<",2)}):
				frappe.throw(_('Journal Entry  <a href="#Form/Journal Entry/{0}">{0}</a> for this transaction needs to be cancelled first').format(self.journal_entry),title='Not permitted')

	def on_submit(self):
		check_budget_available(self.cost_center,self.expense_account,self.posting_date,self.amount,self.business_activity)
		self.post_journal_entry()

	def post_journal_entry(self):
		if not self.amount:
			frappe.throw(_("Amount should be greater than zero"))

		credit_account = self.expense_account
		advance_account = frappe.db.get_value("Company", self.company, "default_bank_account")

		if not credit_account:
			frappe.throw("Expense Account is mandatory")
		if not advance_account:
			frappe.throw("Setup Default Bank Account in Company Settings")

		r = []
		if self.remarks:
			r.append(_("Note: {0}").format(self.remarks))

		remarkss = ("").join(r)

		# Posting Journal Entry
		je = frappe.new_doc("Journal Entry")

		je.update({
			"doctype": "Journal Entry",
			"voucher_type": "Bank Entry",
			"naming_series": "Bank Payment Voucher",
			"title": "Reimbursement - " + self.name,
			"user_remark": remarkss if remarkss else "Note: " + "Reimbursement - " + self.name,
			"posting_date": self.posting_date,
			"company": self.company,
			"total_amount_in_words": money_in_words(self.amount),
			"branch": self.branch
		})

		je.append("accounts",{
			"account": advance_account,
			"credit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"reference_type": "Reimbursement",
			"reference_name": self.name,
			"business_activity": self.business_activity
		})


		je.append("accounts",{
			"account": credit_account,
			"debit_in_account_currency": self.amount,
			"cost_center": self.cost_center,
			"business_activity": self.business_activity
		})

		je.insert()
		#Set a reference to the claim journal entry
		self.db_set("journal_entry",je.name)
		frappe.msgprint(_('Journal Entry <a href="#Form/Journal Entry/{0}">{0}</a> posted to accounts').format(je.name))