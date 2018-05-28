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

class JobCard(AccountsController):
	def validate(self):
		check_future_date(self.posting_date)
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

	def on_submit(self):
		if not self.repair_type:
			frappe.throw("Specify whether the maintenance is Major or Minor")
		if not self.finish_date:
			frappe.throw("Please enter Job Out Date")
		else:
			self.update_reservation()
		self.check_items()
		if self.owned_by == "Own":
			self.db_set("outstanding_amount", 0)
		if self.owned_by == "CDCL":
			self.post_journal_entry()
			self.db_set("outstanding_amount", 0)
		if self.owned_by == "Others":
			self.make_gl_entries()
		self.update_breakdownreport()

	def before_cancel(self):
		docs = check_uncancelled_linked_doc(self.doctype, self.name)
                if docs != 1:
			if str(docs[0]) != "Stock Entry":
				frappe.throw("There is an uncancelled <b>" + str(docs[0]) + "("+ str(docs[1]) +")</b> linked with this document")
		cl_status = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if cl_status and cl_status != 2:
			frappe.throw("You need to cancel the journal entry related to this job card first!")
		
		bdr = frappe.get_doc("Break Down Report", self.break_down_report)
		bdr.db_set("job_card", "")
		self.db_set('jv', "")

	def on_cancel(self):
		if self.owned_by == "Others":
			self.make_gl_entries()	

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

		if goods_account and services_account and receivable_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "Job Card (" + self.name + ")"
			je.voucher_type = 'Maintenance Invoice'
			je.naming_series = 'Maintenance Invoice'
			je.remark = 'Payment against : ' + self.name;
			je.posting_date = self.posting_date
			je.branch = self.branch

			if self.owned_by == "CDCL":
				ir_account = frappe.db.get_single_value("Maintenance Accounts Settings", "hire_revenue_internal_account")
				ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
				if not ic_account:
					frappe.throw("Setup Intra-Company Account in Accounts Settings")	
				if not ir_account:
					frappe.throw("Setup Internal Revenue Account in Maintenance Accounts Settings")	

				je.append("accounts", {
						"account": maintenance_account,
						"reference_type": "Job Card",
						"reference_name": self.name,
						"cost_center": self.customer_cost_center,
						"debit_in_account_currency": flt(self.total_amount),
						"debit": flt(self.total_amount),
					})
				je.append("accounts", {
						"account": ic_account,
						"reference_type": "Job Card",
						"reference_name": self.name,
						"cost_center": self.customer_cost_center,
						"credit_in_account_currency": flt(self.total_amount),
						"credit": flt(self.total_amount),
					})
				je.append("accounts", {
						"account": ic_account,
						"reference_type": "Job Card",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"debit_in_account_currency": flt(self.total_amount),
						"debit": flt(self.total_amount),
					})
				je.append("accounts", {
						"account": ir_account,
						"reference_type": "Job Card",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"credit_in_account_currency": flt(self.total_amount),
						"credit": flt(self.total_amount),
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

        def make_gl_entries(self):
                if self.total_amount:
                        from erpnext.accounts.general_ledger import make_gl_entries
                        gl_entries = []
                        self.posting_date = self.finish_date

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
                                       "cost_center": self.cost_center
                                }, self.currency)
                        )

			if self.goods_amount:
				gl_entries.append(
					self.get_gl_dict({
					       "account": goods_account,
					       "against": self.customer,
					       "credit": self.goods_amount,
					       "credit_in_account_currency": self.goods_amount,
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
					       "cost_center": self.cost_center
					}, self.currency)
				)


                        make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)


	def update_reservation(self):
		frappe.db.sql("update `tabEquipment Reservation Entry` set to_date = %s, to_time = %s where docstatus = 1 and ehf_name = %s", (self.finish_date, self.job_out_time, self.break_down_report))
		frappe.db.commit()

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
		je.posting_date = job.finish_date
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
		target.ref_doc = "Job Card"
		target.net_amount = obj.total_amount
		target.income_account = frappe.db.get_value("Branch", obj.branch, "revenue_bank_account")
	
	doc = get_mapped_doc("Job Card", source_name, {
			"Job Card": {
				"doctype": "Mechanical Payment",
				"field_map": {
					"name": "ref_no",
					"outstanding_amount": "receivable_amount",
				},
				"postprocess": update_docs,
				"validation": {"docstatus": ["=", 1]}
			},
		}, target_doc)
	return doc
