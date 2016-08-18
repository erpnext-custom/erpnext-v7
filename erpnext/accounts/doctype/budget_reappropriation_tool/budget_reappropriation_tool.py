# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate, flt

class BudgetReappropriationTool(Document):
	pass

def budget_check(from_cc=None, from_acc=None, amount=None):
	#Get cost center & target details
	budget = get_cc_acc_budget(from_cc, from_acc)

	if budget:
		for a in budget:
			if flt(amount) <= flt(a.budget_amount):
				return True
			else:
				return False
	else:
		frappe.throw("No budget booked under " + str(from_acc) + " at " + str(from_cc))


def get_cc_acc_budget(cc, acc):
	return frappe.db.sql("""select ba.name, ba.parent, ba.budget_amount
				from `tabBudget` b, `tabBudget Account` ba
				where b.name=ba.parent and b.fiscal_year=%s and b.cost_center = %s and ba.account = %s
				""", (str(nowdate())[0:4], cc, acc), as_dict=True)

@frappe.whitelist()
def reappropriate(from_cc=None, to_cc=None, from_acc=None, to_acc=None, amount=None):
	if(budget_check(from_cc, from_acc, amount)):
		to_account = get_cc_acc_budget(to_cc, to_acc)
		
		if to_account:
			to_budget_account = frappe.get_doc("Budget", to_account[0].parent)
			frappe.throw("Account Found: " + str(to_budget_account))

			to_budget_account.budget_received+=flt(amount)
			to_budget_account.initial_budget = 2000.00
			#to_budget_account.cancel()
			#to_budget_account.submit()
			frappe.throw("Account Found: " + str(to_budget_account.budget_received))
		else:
			frappe.throw("SHITTTTT")
			
			
		app_details = frappe.new_doc("Reappropriation Details")
		app_details.from_cost_center = from_cc
		app_details.to_cost_center = to_cc
		app_details.from_account = from_acc
		app_details.to_account = to_acc
		app_details.amount = amount
		app_details.appropriation_on = nowdate()
		app_details.submit()
	else:
		frappe.throw("You don't have enough budget in " + str(from_acc) + " under " + str(from_cc))

