# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, get_settings_value

class RoyaltyPayment(Document):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_data()

	def validate_data(self):
		if self.production_type == "Planned":
			if not self.marking_list:
				frappe.throw("Marking List is mandatory")
			
			if not self.planned_items:
				frappe.throw("Royalty Details is mandatory")
			self.adhoc_production = None
		else:
			if not self.adhoc_production:
				frappe.throw("Adhoc Production is mandatory")
			self.marking_list = None
			self.planned_items = []

	def get_royalty_details(self):
		if self.production_type == "Planned":
			if not self.marking_list:
				frappe.throw("Marking List is Mandatory")
			entries = frappe.db.sql("select timber_class, timber_type, sum(qty_m3) as qty_m3, sum(qty_cft) as qty_cft, log_rate, log_percent, sum(log_amount) as log_amount, firewood_rate, firewood_percent, sum(firewood_amount) as firewood_amount, sum(royalty_amount) as royalty_amount from `tabMarking List Details` where parent = %s and docstatus = 1 group by timber_class, timber_type order by timber_class", self.marking_list, as_dict=1)

			self.set("planned_items", [])

			total_royalty = total_m3 = total_cft = log_amount = timber_amount = total_log = total_timber = 0
			for d in entries:
				row = self.append('planned_items', {})
				row.update(d)
				total_royalty += d.royalty_amount
				total_m3 += d.qty_m3
				total_cft += d.qty_cft
				log_amount += d.log_amount
				timber_amount += d.firewood_amount 
				total_log = d.qty_cft * d.log_percent / 100
				total_timber = d.qty_m3 * d.firewood_percent / 100

			self.total_royalty = total_royalty
			self.total_m3 = total_m3
			self.total_cft = total_cft
			self.log_amount = log_amount
			self.timber_amount = timber_amount
			self.total_log = total_log
			self.total_timber = total_timber
			frappe
		else:
			if not self.adhoc_production or not self.from_date or not self.to_date:
				frappe.throw("Adhoc Production, From Date and To Date are Mandatory")

	def make_royalty_payment(self):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Royalty payment for (" + self.location + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Payment against : ' + self.name;
		je.posting_date = frappe.utils.nowdate()
		je.branch = self.branch

		royalty_account = frappe.db.get_value("Production Account Settings", self.company, "default_royalty_account")
		if not royalty_account:
			frappe.throw("Setup Default Royalty Account in Production Account Settings")	

		bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not bank_account:
			frappe.throw("Setup Expense Bank Account in Branch")	

		je.append("accounts", {
				"account": royalty_account,
				"reference_type": self.doctype,
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.total_royalty),
				"debit": flt(self.total_royalty),
				"business_activity": self.business_activity
			})

		je.append("accounts", {
				"account": bank_account,
				"reference_type": self.doctype,
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_royalty),
				"credit": flt(self.total_royalty),
				"business_activity": self.business_activity
			})
		je.save()
		self.db_set("journal_entry", je.name)
		frappe.reload_doctype(self.doctype)
