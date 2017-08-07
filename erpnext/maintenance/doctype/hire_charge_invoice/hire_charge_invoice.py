# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate

class HireChargeInvoice(Document):
	def validate(self):
		self.check_advances(self.ehf_name)
		if self.balance_amount < 0:
			frappe.throw("Balance amount cannot be negative")

	def on_submit(self):
		self.update_advance_amount();
		self.update_vlogs(1)
		self.post_journal_entry()

	def on_cancel(self):
		cl_status = frappe.db.get_value("Journal Entry", self.invoice_jv, "docstatus")
		if cl_status != 2:
			frappe.throw("You need to cancel the journal entry ("+ str(self.invoice_jv) + ")related to this invoice first!")
		if self.payment_jv:
			cl_status = frappe.db.get_value("Journal Entry", self.payment_jv, "docstatus")
			if cl_status != 2:
				frappe.throw("You need to cancel the journal entry ("+ str(self.payment_jv) + ")related to this invoice first!")
		self.readjust_advance()
		self.update_vlogs(0)
		self.db_set("invoice_jv", "")
		self.db_set("payment_jv", "")

	def check_advances(self, hire_name):
		advance = frappe.db.sql("select 1 from `tabJournal Entry` t1, `tabJournal Entry Account` t2 where t1.name = t2.parent and t2.is_advance = 'Yes' and t1.docstatus = 1 and t2.reference_name = \'" + str(hire_name)  + "\'", as_dict=True)
		if advance and not self.advances:
			frappe.msgprint("There is a Advance Payment for this Hire Form. You might want to pull it using 'Get Advances' button")


	def update_advance_amount(self):
		lst = []
		for d in self.get('advances'):
			if flt(d.allocated_amount) > 0:
				args = frappe._dict({
					'voucher_type': 'Journal Entry',
					'voucher_no' : d.jv_name,
					'voucher_detail_no' : d.reference_row,
					'against_voucher_type' : self.doctype,
					'against_voucher'  : self.name,
					'account' : d.advance_account,
					'party_type': "Customer",
					'party': self.customer,
					'is_advance' : 'Yes',
					'dr_or_cr' : "credit_in_account_currency",
					'unadjusted_amount' : flt(d.actual_advance_amount),
					'allocated_amount' : flt(d.allocated_amount),
					'exchange_rate': 1,
				})
				lst.append(args)

		if lst:
			from erpnext.accounts.utils import reconcile_against_document
			reconcile_against_document(lst)

	def update_vlogs(self, value):
		for a in self.items:
			logbook = frappe.get_doc("Vehicle Logbook", a.vehicle_logbook)			
			logbook.db_set("invoice_created", value)

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
		advance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_advance_account")
		hire_account = frappe.db.get_single_value("Maintenance Accounts Settings", "hire_revenue_account")

		if hire_account and advance_account and receivable_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "Hire Charge Invoice (" + self.name + ")"
			je.voucher_type = 'Hire Invoice'
			je.naming_series = 'Hire Invoice'
			je.remark = 'Payment against : ' + self.name;
			je.posting_date = self.posting_date
			je.branch = self.branch
			
			if self.total_invoice_amount > 0:
				je.append("accounts", {
						"account": hire_account,
						"reference_type": "Hire Charge Invoice",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"credit_in_account_currency": flt(self.total_invoice_amount),
						"credit": flt(self.total_invoice_amount),
					})

			if self.advance_amount > 0:
				je.append("accounts", {
						"account": advance_account,
						"party_type": "Customer",
						"party": self.customer,
						"reference_type": "Hire Charge Invoice",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"debit_in_account_currency": flt(self.advance_amount),
						"debit": flt(self.advance_amount),
					})

			if self.balance_amount > 0:
				je.append("accounts", {
						"account": receivable_account,
						"party_type": "Customer",
						"party": self.customer,
						"reference_type": "Hire Charge Invoice",
						"reference_name": self.name,
						"cost_center": self.cost_center,
						"debit_in_account_currency": flt(self.balance_amount),
						"debit": flt(self.balance_amount),
					})

			je.submit()
			
			self.db_set("invoice_jv", je.name)

		else:
			frappe.throw("Define Default Accounts in Maintenance Accounts Settings")	

	def readjust_advance(self):
		frappe.db.sql("update `tabJournal Entry Account` set reference_type=%s,reference_name=%s where reference_type=%s and reference_name=%s and docstatus = 1", ("Equipment Hiring Form", self.ehf_name, "Hire Charge Invoice", self.name))
		
@frappe.whitelist()
def get_vehicle_logs(form):
	if form:
		return frappe.db.sql("select a.name, a.equipment, a.equipment_number, a.total_work_time, a.total_idle_time, a.work_rate, a.idle_rate, (select count(1) from `tabVehicle Log` b where b.parent = a.name) as no_of_days from `tabVehicle Logbook` a where a.docstatus = 1 and a.invoice_created = 0 and a.ehf_name = \'" + str(form) + "\'", as_dict=True)
	else:
		frappe.throw("Select Equipment Hiring Form first!")

@frappe.whitelist()
def get_vehicle_accessories(form, equipment):
	if form and equipment:
		data = frappe.db.sql("select accessory1, accessory2, accessory3, accessory4, accessory5, rate1, rate2, rate3, rate4, rate5, irate1, irate2, irate3, irate4, irate5 from `tabHiring Approval Details` where parent = \'" + str(form) + "\' and equipment = \'" + str(equipment) + "\'", as_dict=True)
		accessories = []
		for a in data:
			if a.accessory1:
				accessories.append({"name": a.accessory1, "work": a.rate1, "idle": a.irate1})	
			if a.accessory2:
				accessories.append({"name": a.accessory2, "work": a.rate2, "idle": a.irate2})	
			if a.accessory3:
				accessories.append({"name": a.accessory3, "work": a.rate3, "idle": a.irate3})	
			if a.accessory4:
				accessories.append({"name": a.accessory4, "work": a.rate4, "idle": a.irate4})	
			if a.accessory5:
				accessories.append({"name": a.accessory5, "work": a.rate5, "idle": a.irate5})	
		return accessories
	else:
		frappe.throw("Select Equipment Hiring Form first!")
#Get advances
@frappe.whitelist()
def get_advances(hire_name):
	if hire_name:
		return frappe.db.sql("select t1.name, t1.remark, t2.credit_in_account_currency as amount, t2.account as advance_account, t2.cost_center, t2.name as reference_row from `tabJournal Entry` t1, `tabJournal Entry Account` t2 where t1.name = t2.parent and t2.is_advance = 'Yes' and t1.docstatus = 1 and t2.reference_name = \'" + str(hire_name)  + "\'", as_dict=True)
	else:
		frappe.throw("Select Equipment Hiring Form first!")

@frappe.whitelist()
def make_bank_entry(frm=None):
	if frm:
		invoice = frappe.get_doc("Hire Charge Invoice", frm)
		revenue_bank_account = frappe.db.get_value("Branch", invoice.branch, "revenue_bank_account")
		receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
		if not revenue_bank_account:
			frappe.throw("Setup Default Revenue Bank Account for your Branch")
		if not receivable_account:
			frappe.throw("Setup Default Receivable Account in Maintenance Setting")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Payment for Hire Charge Invoice (" + invoice.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Receipt Voucher'
		je.remark = 'Payment Received against : ' + invoice.name;
		je.posting_date = invoice.posting_date
		total_amount = invoice.total_invoice_amount
		je.branch = self.branch

		je.append("accounts", {
				"account": receivable_account,
				"party_type": "Customer",
				"party": invoice.customer,
				"reference_type": "Hire Charge Invoice",
				"reference_name": invoice.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(total_amount),
				"credit": flt(total_amount),
			})

		je.append("accounts", {
				"account": revenue_bank_account,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(total_amount),
				"debit": flt(total_amount),
			})

		je.insert()

		invoice.db_set("payment_jv", je.name)
		frappe.msgprint("Bill processed to accounts through journal voucher " + je.name)
		return "D"
	else:
		frappe.msgprint("Bill NOT processed")
		return "NO"
