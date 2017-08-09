# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import time_diff_in_hours
from frappe.utils import cstr, flt, fmt_money, formatdate

class JobCard(Document):
	def validate(self):
		self.update_breakdownreport()
		#Amount Segregation
		cc_amount = {}
		self.services_amount = self.goods_amount = 0;
		for a in self.items:
			if cc_amount.has_key(a.which):
				cc_amount[a.which] = cc_amount[cc] + a.amount
			else:
				cc_amount[a.which] = a.amount;
		if cc_amount.has_key('Services'):
			self.services_amount = cc_amount['Services']
		if cc_amount.has_key('Goods'):
			self.goods_amount = cc_amount['Goods']
		self.total_amount = flt(self.services_amount) + flt(self.goods_amount)

	def on_submit(self):
		self.check_items()
		self.post_journal_entry()
		self.update_breakdownreport()

	def before_cancel(self):
		cl_status = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if cl_status != 2:
			frappe.throw("You need to cancel the journal entry related to this job card first!")
		
		bdr = frappe.get_doc("Break Down Report", self.break_down_report)
		bdr.db_set("job_card", "")
		self.db_set('jv', "")

	def get_default_settings(self):
		goods_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_goods_account")
		services_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_services_account")
		receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
		maintenance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "maintenance_expense_account")

		return goods_account, services_account, receivable_account, maintenance_account

	def check_items(self):
		if not self.items:
			frappe.throw("Cannot submit job card with empty job details")
		else:
			for a in self.items:
				if flt(a.amount) == 0: 
					frappe.throw("Cannot submit job card without cost details")

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		goods_account, services_account, receivable_account, maintenance_account = self.get_default_settings()

		if goods_account and services_account and receivable_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "Job Card (" + self.name + ")"
			je.voucher_type = 'Maintenance Invoice'
			je.naming_series = 'Maintenance Invoice'
			je.remark = 'Payment against : ' + self.name;
			je.posting_date = self.posting_date
			je.branch = self.branch

			for a in ["Services", "Goods"]:
				account_name = goods_account
				amount = self.goods_amount
				if a == "Services":
					amount = self.services_amount
					account_name = services_account;
				if amount != 0:
					je.append("accounts", {
							"account": account_name,
							"reference_type": "Job Card",
							"reference_name": self.name,
							"cost_center": self.cost_center,
							"credit_in_account_currency": flt(amount),
							"credit": flt(amount),
						})

			if self.owned_by == "Own":
				je.append("accounts", {
						"account": maintenance_account,
						"reference_type": "Job Card",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"debit_in_account_currency": flt(self.total_amount),
						"debit": flt(self.total_amount),
					})
				je.insert()
			else:
				je.append("accounts", {
						"account": receivable_account,
						"party_type": "Customer",
						"party": self.customer,
						"reference_type": "Job Card",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"debit_in_account_currency": flt(self.total_amount),
						"debit": flt(self.total_amount),
					})
				je.submit()
			
			self.db_set("jv", je.name)
		else:
			frappe.throw("Setup Default Goods, Services and Receivable Accounts in Maintenance Accounts Settings")

	##
	# Update the job card reference on Break Down Report
	##
	def update_breakdownreport(self):
		bdr = frappe.get_doc("Break Down Report", self.break_down_report)
		bdr.db_set("job_card", self.name)

@frappe.whitelist()
def make_bank_entry(frm=None):
	if frm:
		job = frappe.get_doc("Job Card", frm)
		revenue_bank_account = frappe.db.get_value("Branch", job.branch, "revenue_bank_account")
		receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
		if not revenue_bank_account:
			frappe.throw("Setup Default Revenue Bank Account for your Branch")
		if not receivable_account:
			frappe.throw("Setup Default Receivable Account in Maintenance Setting")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Payment for Job Card (" + job.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Receipt Voucher'
		je.remark = 'Payment Received against : ' + job.name;
		je.posting_date = job.posting_date
		total_amount = job.total_amount
		je.branch = job.branch
	
		je.append("accounts", {
				"account": revenue_bank_account,
				"cost_center": job.cost_center,
				"debit_in_account_currency": flt(total_amount),
				"debit": flt(total_amount),
			})
		
		je.append("accounts", {
				"account": receivable_account,
				"party_type": "Customer",
				"party": job.customer,
				"reference_type": "Job Card",
				"reference_name": job.name,
				"cost_center": job.cost_center,
				"credit_in_account_currency": flt(total_amount),
				"credit": flt(total_amount),
			})

		je.insert()

		job.db_set("payment_jv", je.name)
		frappe.msgprint("Bill processed to accounts through journal voucher " + je.name)
		return "D"
	else:
		frappe.msgprint("Bill NOT processed")
		return "NO"
