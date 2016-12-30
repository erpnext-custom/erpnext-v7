# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AssetModifierTool(Document):
	pass

##
# Method call from client to perform reappropriation
##
@frappe.whitelist()
def change_value(asset=None, value=None):
	if(asset and value):
		asset_obj = = frappe.get_doc("Asset", asset)

		if asset_obj:
			frappe.throw(str(asset_obj.name) + " " + str(asset_obj.gross_purchase_amount) + " " + str(asset_obj.asset_account) + " " + str(asset_obj.schedules)  )
			#Deduct in the From Account and Cost Center
			"""from_budget_account = frappe.get_doc("Budget Account", from_account[0].name)
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
			app_details.submit() """

			return "DONE"

		else:
			return "Invalid asset code"

	elif not asset:
		return "Invalid asset code"

	elif not value:
		return "Invalid asset value"
	else:
		return "Sorry, something happened. Please try again"
