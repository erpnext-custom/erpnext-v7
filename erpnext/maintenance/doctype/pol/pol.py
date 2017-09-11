# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate

class POL(Document):
	def validate(self):
		pass

	def on_submit(self):
		if self.direct_consumption:
			self.consume_pol()
		self.post_journal_entry()
	
	def on_cancel(self):
		docstatus = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if docstatus != 2:
			frappe.throw("Cancel the Journal Entry " + str(self.jv) + " and proceed.")
	
		doc = frappe.get_doc("Consumed POL", self.consumed)
		doc.db_set("docstatus", 2)
		
		self.db_set("consumed", "")
		self.db_set("jv", "")
	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		veh_cat = frappe.db.get_value("Equipment", self.equipment, "equipment_category")
		if veh_cat:
			if veh_cat == "Pool Vehicle":
				pol_account = frappe.db.get_single_value("Maintenance Accounts Settings", "pool_vehicle_pol_expenses")
			else:
				pol_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_pol_expense_account")
		else:
			frappe.throw("Can not determine machine category")
		#expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		expense_bank_account = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "default_payable_account")
		if not expense_bank_account:
 			frappe.throw("No Default Payable Account set in Company")

		if expense_bank_account and pol_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "POL (" + self.pol_type + " for " + self.equipment_number + ")"
			je.voucher_type = 'Bank Entry'
			je.naming_series = 'Bank Payment Voucher'
			je.remark = 'Payment against : ' + self.name;
			je.posting_date = self.date
			je.branch = self.branch

			je.append("accounts", {
					"account": pol_account,
					"cost_center": self.cost_center,
					"reference_type": "POL",
					"reference_name": self.name,
					"debit_in_account_currency": flt(self.total_amount),
					"debit": flt(self.total_amount),
				})

			je.append("accounts", {
					"account": expense_bank_account,
					"cost_center": self.cost_center,
					"party_type": "Supplier",
					"party": self.supplier,
					"credit_in_account_currency": flt(self.total_amount),
					"credit": flt(self.total_amount),
				})

			je.insert()
			self.db_set("jv", je.name)
		else:
			frappe.throw("Define POL expense account in Maintenance Setting or Expense Bank in Branch")
		
	def consume_pol(self):
		con = frappe.new_doc("Consumed POL")	
		con.equipment = self.equipment
		con.pol_type = self.pol_type
		con.branch = self.branch
		con.date = self.date
		con.qty = self.qty
		con.submit()
		self.db_set("consumed", con.name)


