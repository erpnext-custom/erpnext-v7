# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class LeaveTravelConcession(Document):
	def validate(self):
		pass

	def on_submit(self):
		cc_amount = {}
		for a in self.items:
			cc = frappe.db.get_value("Employee", a.employee, "cost_center")
			if cc_amount.has_key(cc):
				cc_amount[cc] = cc_amount[cc] + a.amount
			else:
				cc_amount[cc] = a.amount;
		
		self.post_journal_entry(cc_amount)

	def post_journal_entry(self, cc_amount):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "LTC (" + self.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'LTC payment against : ' + self.name;
		je.posting_date = self.posting_date
		je.branch = self.branch

		ltc_account = frappe.db.get_single_value("HR Accounts Settings", "ltc_account")
		if not ltc_account:
			frappe.throw("Setup LTC Account in HR Accounts Settings")

		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not expense_bank_account:
			frappe.throw("Setup Expense Bank Account in Branch")

		for key in cc_amount.keys():
			je.append("accounts", {
					"account": ltc_account,
					"reference_type": "Leave Travel Concession",
					"reference_name": self.name,
					"cost_center": key,
					"debit_in_account_currency": flt(cc_amount[key]),
					"debit": flt(cc_amount[key]),
				})
		
			je.append("accounts", {
					"account": expense_bank_account,
					"reference_type": "Leave Travel Concession",
					"reference_name": self.name,
					"cost_center": key,
					"credit_in_account_currency": flt(cc_amount[key]),
					"credit": flt(cc_amount[key]),
				})

		je.insert()

		self.db_set("journal_entry", je.name)

	def on_cancel(self):
		jv = frappe.db.get_value("Journal Entry", self.journal_entry, "docstatus")
		if jv != 2:
			frappe.throw("Can not cancel LTC without canceling the corresponding journal entry " + str(self.journal_entry))
		else:
			self.db_set("journal_entry", "")


@frappe.whitelist()
def get_ltc_details(branch=None):
	query = "select b.employee, b.employee_name, b.branch, a.amount from `tabSalary Detail` a, `tabSalary Structure` b where a.parent = b.name and a.salary_component = 'Basic Pay' and b.is_active = 'Yes' and b.eligible_for_ltc = 1 "
	if branch:
		query += " and b.branch = \'" + str(branch) + "\'";
	query += " order by b.branch"
	return frappe.db.sql(query, as_dict=True)
