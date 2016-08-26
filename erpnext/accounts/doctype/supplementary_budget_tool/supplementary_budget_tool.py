# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import nowdate, flt

class SupplementaryBudgetTool(Document):
	pass

##
# Get budget details from CC and Account
##
def get_cc_acc_budget(cc, acc):
	return frappe.db.sql("""select ba.name, ba.parent, ba.budget_amount
				from `tabBudget` b, `tabBudget Account` ba
				where b.name=ba.parent and b.fiscal_year=%s and b.cost_center = %s and ba.account = %s
				""", (str(nowdate())[0:4], cc, acc), as_dict=True)

##
# Perform the actual budget supplement
##
def do_reappropriate(supplement, total, name, parent):
	query = "update `tabBudget Account` set supplementary_budget = " + str(supplement) + ", budget_amount = " + str(total) + " where name = \'" + str(name) + "\' and parent = \'" + str(parent) + "\'"

	frappe.db.sql(query, auto_commit=1)

##
# Method call from client to perform budget supplement
##
@frappe.whitelist()
def supplement(to_cc=None, to_acc=None, amount=None):
	to_account = get_cc_acc_budget(to_cc, to_acc)	
	if to_account:
		#Add in the To Account and Cost Center
		to_budget_account = frappe.get_doc("Budget Account", to_account[0].name)
		supplement = flt(to_budget_account.supplementary_budget) + flt(amount)
		total = flt(to_budget_account.budget_amount) + flt(amount)
		to_budget_account.set_db("supplementary_budget", supplement)
		to_budget_account.set_db("budget_amount", total)
		#do_reappropriate(supplement, total, to_budget_account.name, to_budget_account.parent)
	
		#Add the reappropriation details for record 
		supp_details = frappe.new_doc("Supplementary Details")
		supp_details.to_cc = to_cc
		supp_details.to_acc = to_acc
		supp_details.amount = amount
		supp_details.posted_date = nowdate()
		supp_details.submit()
			
		return "DONE"

	else:
		return "The budget head you specified doesn't exist. Please try again"

