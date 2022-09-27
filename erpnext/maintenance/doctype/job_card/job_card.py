# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.data import time_diff_in_hours
from frappe.utils import cstr, flt, fmt_money, formatdate, nowdate
from frappe.model.mapper import get_mapped_doc
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import check_uncancelled_linked_doc, check_future_date
from erpnext.maintenance.maintenance_utils import get_equipment_ba
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba

class JobCard(AccountsController):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_owned_by()
		if self.finish_date:
			check_future_date(self.finish_date)
		self.update_breakdownreport()
		#Amount Segregation
		cc_amount = {}
		self.services_amount = self.goods_amount = 0;
		for a in self.items:
			if cc_amount.has_key(a.which):
				cc_amount[a.which] = flt(cc_amount[a.which]) + flt(a.amount)
			else:
				cc_amount[a.which] = flt(a.amount);
		if cc_amount.has_key('Service'):
			self.services_amount = cc_amount['Service']
		if cc_amount.has_key('Item'):
			self.goods_amount = cc_amount['Item']
		self.total_amount = flt(self.services_amount) + flt(self.goods_amount)
		self.outstanding_amount = self.total_amount

	def validate_owned_by(self):
		if self.owned_by == "Own Company" and self.cost_center == self.customer_cost_center:
			self.owned_by = "Own Branch"
			self.customer_cost_center = None
			self.customer_branch = None

	def on_submit(self):
		self.validate_owned_by()
		self.check_items()
		if not self.repair_type:
			frappe.throw("Specify whether the maintenance is Major or Minor")
		if not self.finish_date:
			frappe.throw("Please enter Job Out Date")
		else:
			if self.finish_date < self.posting_date:
				frappe.throw("Job Out Date should be greater than or equal to Job In Date")
			self.update_reservation()
		#self.check_items()
  		'''
		if self.owned_by == "Own Branch":
			self.db_set("outstanding_amount", 0)
		if self.owned_by == "Own Company" and self.out_source == 0:
			self.post_journal_entry()
			self.db_set("outstanding_amount", 0)
		if self.owned_by == "Others" and self.out_source == 0:
			self.make_gl_entries()
		'''
  
		if self.supplier and self.out_source == 1:
			self.make_gl_entry()

		self.update_breakdownreport()

	def before_cancel(self):
		check_uncancelled_linked_doc(self.doctype, self.name)
		cl_status = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if cl_status and cl_status != 2:
			frappe.throw("You need to cancel the journal entry related to this job card first!")
		
		self.db_set('jv', None)

	def on_cancel(self):
		bdr = frappe.get_doc("Break Down Report", self.break_down_report)
		if bdr.job_card == self.name:
			bdr.db_set("job_card", None)
		if self.owned_by == "Others":
			self.make_gl_entries()
		if self.supplier and self.out_source == 1:
			self.make_gl_entry()	

	def get_default_settings(self):
		goods_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_goods_account")
		services_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_services_account")
		receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
		# maintenance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "maintenance_expense_account")
		equipment_category = frappe.db.get_value("Equipment",{"equipment_number":self.equipment_number},"equipment_category")
		maintenance_account = frappe.db.get_value("Equipment Category",equipment_category,"expense_account")

		return goods_account, services_account, receivable_account, maintenance_account
		# return goods_account, services_account, receivable_account

	def check_items(self):
		if not self.items:
			frappe.throw("Cannot submit job card with empty job details")
		else:
			for a in self.items:
				if self.out_source == 1:
					if flt(a.amount) == 0: 
						frappe.throw("Cannot submit job card without cost details")
				
	def get_job_items(self):
		items = frappe.db.sql("select se.name as stock_entry, sed.item_code as job, sed.item_name as job_name, sed.qty as quantity, sed.amount from `tabStock Entry Detail` sed, `tabStock Entry` se where se.docstatus = 1 and sed.parent = se.name and se.purpose = \'Material Issue\' and se.job_card = \'"+ str(self.name) +"\'", as_dict=True)

		if items:
			#self.set('items', [])
			for d in items:
				already = False
				
				for a in self.items:
					if a.stock_entry == d.stock_entry and a.job == d.job and a.job_name == d.job_name and a.quantity == d.quantity:
						already = True
				if not already:
					d.which = "Item"
					row = self.append('items', {})
					row.update(d)
		else:
			frappe.msgprint("No stock entries related to the job card found. Entries might not have been submitted?")

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		goods_account, services_account, receivable_account, maintenance_account = self.get_default_settings()
		# goods_account, services_account, receivable_account = self.get_default_settings()

		if goods_account and services_account and receivable_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "Job Card (" + self.name + ")"
			je.voucher_type = 'Maintenance Invoice'
			je.naming_series = 'Maintenance Invoice'
			je.remark = 'Payment against : ' + self.name;
			je.posting_date = self.posting_date
			je.branch = self.branch

			if self.owned_by == "Own Company":
				ir_account = frappe.db.get_single_value("Maintenance Accounts Settings", "hire_revenue_internal_account")
				if not ir_account:
					frappe.throw("Setup Internal Revenue Account in Maintenance Accounts Settings")	

				if not self.equipment:
					frappe.throw("Equipment is Mandatory")
				ba = get_equipment_ba(self.equipment)
				default_ba = get_default_ba()

				je.append("accounts", {
						"account": maintenance_account,
						"reference_type": "Job Card",
						"reference_name": self.name,
						"cost_center": self.customer_cost_center,
						"debit_in_account_currency": flt(self.total_amount),
						"debit": flt(self.total_amount),
						"business_activity": ba
					})

				for a in ["Service", "Item"]:
					account_name = goods_account
					amount = self.goods_amount
					if a == "Service":
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
								"business_activity": ba
							})

				allow_inter_company_transaction = frappe.db.get_single_value("Accounts Settings", "auto_accounting_for_inter_company")
				if allow_inter_company_transaction:
					ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
					if not ic_account:
						frappe.throw("Setup Intra-Company Account in Accounts Settings")	

					je.append("accounts", {
							"account": ic_account,
							"reference_type": "Job Card",
							"reference_name": self.name,
							"cost_center": self.customer_cost_center,
							"credit_in_account_currency": flt(self.total_amount),
							"credit": flt(self.total_amount),
							"business_activity": default_ba
						})
					je.append("accounts", {
							"account": ic_account,
							"reference_type": "Job Card",
							"reference_name": self.name,
							"cost_center": self.cost_center,
							"debit_in_account_currency": flt(self.total_amount),
							"debit": flt(self.total_amount),
							"business_activity": default_ba
						})
				je.insert()

			else:
				for a in ["Service", "Item"]:
					account_name = goods_account
					amount = self.goods_amount
					if a == "Service":
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

				if self.owned_by == "Own Branch":
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

		def make_gl_entries(self):
			if self.total_amount:
					from erpnext.accounts.general_ledger import make_gl_entries
					gl_entries = []
					self.posting_date = self.finish_date
			ba = get_default_ba()

			goods_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_goods_account")
			services_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_services_account")
			receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
			if not goods_account:
				frappe.throw("Setup Default Goods Account in Maintenance Setting")
			if not services_account:
				frappe.throw("Setup Default Services Account in Maintenance Setting")
			if not receivable_account:
				frappe.throw("Setup Default Receivable Account in Maintenance Setting")
						
			gl_entries.append(
					self.get_gl_dict({
						   "account":  receivable_account,
						   "party_type": "Customer",
						   "party": self.customer,
						   "against": receivable_account,
						   "debit": self.total_amount,
						   "debit_in_account_currency": self.total_amount,
						   "against_voucher": self.name,
						   "against_voucher_type": self.doctype,
						   "cost_center": self.cost_center,
						   "business_activity": ba
					}, self.currency)
			)

			if self.goods_amount:
				gl_entries.append(
					self.get_gl_dict({
						   "account": goods_account,
						   "against": self.customer,
						   "credit": self.goods_amount,
						   "credit_in_account_currency": self.goods_amount,
						   "business_activity": ba,
						   "cost_center": self.cost_center
					}, self.currency)
				)
			if self.services_amount:
				gl_entries.append(
					self.get_gl_dict({
						   "account": services_account,
						   "against": self.customer,
						   "credit": self.services_amount,
						   "credit_in_account_currency": self.services_amount,
						   "business_activity": ba,
						   "cost_center": self.cost_center
					}, self.currency)
				)


			make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)

	def make_gl_entry(self):
		if self.total_amount:
			from erpnext.accounts.general_ledger import make_gl_entries
			gl_entries = []
			self.posting_date = self.finish_date
			ba = get_default_ba()
			# maintenance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "maintenance_expense_account")
			payable_account = frappe.db.get_value("Company", "Natural Resources Development Corporation Ltd","default_payable_account")
			equipment_category = frappe.db.get_value("Equipment",{"equipment_number":self.equipment_number},"equipment_category")
		
			maintenance_account = frappe.db.get_value("Equipment Category",equipment_category,"expense_account")
			if not maintenance_account:
					frappe.throw("Setup Default Maintenace Expense Account in Equipment Category")
			if not payable_account:
					frappe.throw("Setup Default Payable Account in Company Setting")

			gl_entries.append(
					self.get_gl_dict({
						   "account":  maintenance_account,
						   "against": self.supplier,
						   "debit": self.total_amount,
						   "debit_in_account_currency": self.total_amount,
						   "against_voucher": self.name,
						   "against_voucher_type": self.doctype,
						   "cost_center": self.cost_center,
						   "business_activity": ba
					}, self.currency)
				)
			gl_entries.append(
					self.get_gl_dict({
							"account": payable_account,
							"party_type": "Supplier",
							"party": self.supplier,
							"against": self.supplier,
							"credit": self.total_amount,
							"credit_in_account_currency": self.total_amount,
							"business_activity": ba,
							"cost_center": self.cost_center
					}, self.currency))


			make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="Yes", merge_entries=False)

	def update_reservation(self):
		frappe.db.sql("update `tabEquipment Reservation Entry` set to_date = %s, to_time = %s where docstatus = 1 and ehf_name = %s", (self.finish_date, self.job_out_time, self.break_down_report))
		frappe.db.sql("update `tabEquipment Status Entry` set to_date = %s, to_time = %s where docstatus = 1 and ehf_name = %s", (self.finish_date, self.job_out_time, self.break_down_report))
		#frappe.db.commit()

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
		expense_bank_account = frappe.db.get_value("Branch", job.branch, "expense_bank_account")
		expense_account = frappe.db.get_single_value("Maintenance Accounts Settings", "maintenance_expense_account")
		if not expense_bank_account:
			frappe.throw("Setup Default expense Bank Account for your Branch")
		if not expense_account:
			frappe.throw("Setup maintenance expense Account in Maintenance Setting")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Payment for Job Card (" + job.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Receipt Voucher'
		je.remark = 'Payment Received against : ' + job.name;
		je.posting_date = job.finish_date
		total_amount = job.total_amount
		je.branch = job.branch
	
		je.append("accounts", {
				"account": expense_bank_account,
				"cost_center": job.cost_center,
				"debit_in_account_currency": flt(total_amount),
				"debit": flt(total_amount),
			})
		
		je.append("accounts", {
				"account": expense_account,
				"party_type": "Supplier",
				"party": job.supplier,
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


#Deprecated to accomodate more than one MIN
@frappe.whitelist()
def get_min_items(name):
	doc = frappe.get_doc("Stock Entry", name)	
	if doc:
		if doc.docstatus != 1:
			frappe.throw("Can only get items from Submitted Entries")
		else:
			result = []
			for a in doc.items:
				row = {
					"item_code": a.item_code,
					"item_name": a.item_name,
					"qty": a.qty,
					"amount": a.amount
				}
				result.append(row)
			return result

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None): 
	def update_docs(obj, target, source_parent):
		target.posting_date = nowdate()
		target.payment_for = "Job Card"
		target.net_amount = obj.outstanding_amount
		target.actual_amount = obj.outstanding_amount
		target.income_account = frappe.db.get_value("Branch", obj.branch, "revenue_bank_account")
		
		target.append("items", {
				"reference_type": "Job Card",
				"reference_name": obj.name,
				"outstanding_amount": obj.outstanding_amount,
				"allocated_amount": obj.outstanding_amount
		})
	
	doc = get_mapped_doc("Job Card", source_name, {
			"Job Card": {
				"doctype": "Mechanical Payment",
				"field_map": {
					"outstanding_amount": "receivable_amount",
				},
				"postprocess": update_docs,
				"validation": {"docstatus": ["=", 1]}
			},
		}, target_doc)
	return doc

@frappe.whitelist()
def make_payment(source_name, target_doc=None):
		def update_docs(obj, target, source_parent):
				target.posting_date = nowdate()
				target.payment_for = "Job Card"
				target.net_amount = obj.total_amount
				target.actual_amount = obj.total_amount
				target.outgoing_account = frappe.db.get_value("Branch", obj.branch, "revenue_bank_account")
				target.supplier = obj.supplier
				target.append("items", {
						"reference_type": "Job Card",
						"reference_name": obj.name,
						"outstanding_amount": obj.total_amount,
						"allocated_amount": obj.total_amount
				})

		doc = get_mapped_doc("Job Card", source_name, {
						"Job Card": {
								"doctype": "Mechanical Payment",
								"field_map": {
										"total_amount": "payable_amount",
								},
								"postprocess": update_docs,
								"validation": {"docstatus": ["=", 1]}
						},
				}, target_doc)
		return doc

