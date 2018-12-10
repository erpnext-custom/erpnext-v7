# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate, flt
from erpnext.custom_utils import check_budget_available

class BudgetReappropiation(Document):
	def validate(self):
		for a in self.items:
			if not flt(a.amount) > 0:
				frappe.throw("Amount should be greater than 0 on row " + str(a.idx))
			if self.from_cost_center == self.to_cost_center and a.from_account == a.to_account:
				frappe.throw("From and To Account cannot be same")
	def on_submit(self):
		self.budget_check()
		for a in self.items:
			self.reappropriate(a.from_account, a.to_account, a.amount, False)

	def on_cancel(self):
		for a in self.items:
			self.reappropriate(a.from_account, a.to_account, a.amount, True)

	##
	# Check the budget amount in the from cost center and account
	##
	def budget_check(self):
		#Get cost center & target details
		budgets = frappe.db.sql("select from_account, sum(amount) as amount from `tabBudget Reappropiation Detail` where parent = %s group by from_account", self.name, as_dict=True)
		for a in budgets:
			check_budget_available(self.from_cost_center, a.from_account, str(self.fiscal_year) + "-01-01", a.amount)

	##
	# Get budget details from CC and Account
	##
	def get_cc_acc_budget(self, cc, acc, fiscal_year):
		if frappe.db.get_value("Fiscal Year", fiscal_year, "closed"):
			frappe.throw("Fiscal Year " + fiscal_year + " has already been closed")
		else:
			return frappe.db.sql("""select ba.name, ba.parent, ba.budget_amount
					from `tabBudget` b, `tabBudget Account` ba
					where b.name=ba.parent and b.fiscal_year=%s and b.cost_center = %s and ba.account = %s and b.docstatus = 1
					""", (fiscal_year, cc, acc), as_dict=True)

	##
	# Method call from client to perform reappropriation
	##
	def reappropriate(self, from_acc=None, to_acc=None, amount=None, cancel=None):
		from_cc = self.from_cost_center
		to_cc = self.to_cost_center
		fiscal_year = self.fiscal_year

		to_account = self.get_cc_acc_budget(to_cc, to_acc, fiscal_year)
		from_account = self.get_cc_acc_budget(from_cc, from_acc, fiscal_year)

		if to_account and from_account:
			#Deduct in the From Account and Cost Center
			from_budget_account = frappe.get_doc("Budget Account", from_account[0].name)
			sent = flt(from_budget_account.budget_sent) + flt(amount)
			total = flt(from_budget_account.budget_amount) - flt(amount)
			if cancel:
				sent = flt(from_budget_account.budget_sent) - flt(amount)
				total = flt(from_budget_account.budget_amount) + flt(amount)
			from_budget_account.db_set("budget_sent", sent)
			from_budget_account.db_set("budget_amount", total)
			
			#Add in the To Account and Cost Center
			to_budget_account = frappe.get_doc("Budget Account", to_account[0].name)
			received = flt(to_budget_account.budget_received) + flt(amount)
			total = flt(to_budget_account.budget_amount) + flt(amount)
			if cancel:
				received = flt(to_budget_account.budget_received) - flt(amount)
				total = flt(to_budget_account.budget_amount) - flt(amount)
			to_budget_account.db_set("budget_received", received)
			to_budget_account.db_set("budget_amount", total)
		
			#Add the reappropriation details for record
			if cancel:
				frappe.db.sql("delete from `tabReappropriation Details` where ref_doc=%s", self.name)
			else:
				app_details = frappe.new_doc("Reappropriation Details")
				app_details.flags.ignore_permissions = 1
				app_details.from_cost_center = from_cc
				app_details.to_cost_center = to_cc
				app_details.from_account = from_acc
				app_details.to_account = to_acc
				app_details.amount = amount
				app_details.appropriation_on = nowdate()
				app_details.ref_doc = self.name
				app_details.submit()
			
			return "DONE"

		elif not to_account:
			frappe.throw("Check your TO Cost Center and Account and try again")
			
		elif not from_account:
			frappe.throw("Check your From Cost Center and Account and try again")
		else:
			frappe.throw("Sorry, something happened. Please try again")



