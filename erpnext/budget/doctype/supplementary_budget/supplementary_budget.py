# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_utils import check_future_date
from frappe.utils import flt, nowdate

class SupplementaryBudget(Document):
	def validate(self):
		check_future_date(self.posting_date)
		self.check_amount()

	def check_amount(self):
		for a in self.items:
			if a.amount <= 0:
				frappe.throw("Amount should be greater than 0 on line " + str(a.idx))

	def on_submit(self):
		for a in self.items:
			self.supplement(a.account, a.amount, str(self.posting_date)[0:4])

	def on_cancel(self):
		for a in self.items:
			self.supplement(a.account, a.amount, str(self.posting_date)[0:4])

	##
	# Get budget details from CC and Account
	##
	def get_cc_acc_budget(self, acc, fiscal_year):
		if frappe.db.get_value("Fiscal Year", fiscal_year, "closed"):
			frappe.throw("Fiscal Year " + fiscal_year + " has already been closed")
		else:
			return frappe.db.sql("""select ba.name, ba.parent, ba.budget_amount
					from `tabBudget` b, `tabBudget Account` ba
					where b.name=ba.parent and b.fiscal_year=%s and b.cost_center = %s and ba.account = %s and b.docstatus = 1
					""", (fiscal_year, self.cost_center, acc), as_dict=True)

	##
	# Method call from client to perform budget supplement
	##
	def supplement(self, to_acc=None, amount=None, fiscal_year=None):
		to_cc = self.cost_center
		to_account = self.get_cc_acc_budget(to_acc, fiscal_year)	
		if to_account:
			#Add in the To Account and Cost Center
			to_budget_account = frappe.get_doc("Budget Account", to_account[0].name)
			if self.docstatus == 1:
				supplement = flt(to_budget_account.supplementary_budget) + flt(amount)
				total = flt(to_budget_account.budget_amount) + flt(amount)
			if self.docstatus == 2:
				supplement = flt(to_budget_account.supplementary_budget) - flt(amount)
				total = flt(to_budget_account.budget_amount) - flt(amount)
			to_budget_account.db_set("supplementary_budget", supplement)
			to_budget_account.db_set("budget_amount", total)
		
			
			if self.docstatus == 1:
				#Add the reappropriation details for record 
				supp_details = frappe.new_doc("Supplementary Details")
				supp_details.flags.ignore_permissions = 1
				supp_details.to_cc = to_cc
				supp_details.to_acc = to_acc
				supp_details.amount = amount
				supp_details.posted_date = nowdate()
				supp_details.ref_doc = self.name
				supp_details.submit()
			if self.docstatus == 2:
				frappe.db.sql("delete from `tabSupplementary Details` where ref_doc = %s", self.name)
		else:
			frappe.throw("The budget head you specified doesn't exist. Please try again")


