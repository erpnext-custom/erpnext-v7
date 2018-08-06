# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate, flt

class BudgetReappropriationTool(Document):
	pass

##
# Check the budget amount in the from cost center and account
##
def budget_check(from_cc=None, from_acc=None, amount=None, fiscal_year=None):
	#Get cost center & target details
	budget = get_cc_acc_budget(from_cc, from_acc, fiscal_year)

	if budget:
		for a in budget:
			if flt(amount) <= flt(a.budget_amount):
				return True
			else:
				return False
	else:
		frappe.throw("No budget booked under " + str(from_acc) + " at " + str(from_cc))

##
# Get budget details from CC and Account
##
def get_cc_acc_budget(cc, acc, fiscal_year):
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
@frappe.whitelist()
def reappropriate(from_cc=None, to_cc=None, from_acc=None, to_acc=None, amount=None, fiscal_year=None):
	if(budget_check(from_cc, from_acc, amount, fiscal_year)):
		to_account = get_cc_acc_budget(to_cc, to_acc, fiscal_year)
		from_account = get_cc_acc_budget(from_cc, from_acc, fiscal_year)

		if to_account and from_account:
			#Deduct in the From Account and Cost Center
			from_budget_account = frappe.get_doc("Budget Account", from_account[0].name)
			sent = flt(from_budget_account.budget_sent) + flt(amount)
			total = flt(from_budget_account.budget_amount) - flt(amount)
			from_budget_account.db_set("budget_sent", sent)
			from_budget_account.db_set("budget_amount", total)
			
			#Add in the To Account and Cost Center
			to_budget_account = frappe.get_doc("Budget Account", to_account[0].name)
			received = flt(to_budget_account.budget_received) + flt(amount)
			total = flt(to_budget_account.budget_amount) + flt(amount)
			to_budget_account.db_set("budget_received", received)
			to_budget_account.db_set("budget_amount", total)
		
			#Add the reappropriation details for record 
			app_details = frappe.new_doc("Reappropriation Details")
			app_details.from_cost_center = from_cc
			app_details.to_cost_center = to_cc
			app_details.from_account = from_acc
			app_details.to_account = to_acc
			app_details.amount = amount
			app_details.appropriation_on = nowdate()
			app_details.submit()
			
			return "DONE"

		elif not to_account:
			return "Check your TO Cost Center and Account and try again"
			
		elif not from_account:
			return "Check your From Cost Center and Account and try again"
		else:
			return "Sorry, something happened. Please try again"

	else:
			return "You don't have enough budget in " + str(from_acc) + " under " + str(from_cc)

"""##
i@frappe.whitelist()
def change():
	doclist = frappe.get_all("Sales Invoice", fields={'name', 'posting_date', 'sales_invoice_date'})
	for doc in doclist:
		to_budget_account = frappe.get_doc("Sales Invoice", doc.name)
		to_budget_account.db_set("sales_invoice_date", doc.posting_date)
		to_budget_account.db_set("posting_date", doc.sales_invoice_date)
	frappe.msgprint("DONE")
"""
