# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.accounts.general_ledger import make_gl_entries
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import check_future_date

class DirectPayment(AccountsController):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_data()
		self.clearance_date = None
		self.allow_deduction_only_for_single_party()

	def on_submit(self):
		self.post_gl_entry()
		self.consume_budget()

	def on_cancel(self):
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		self.post_gl_entry()
		self.cancel_budget_entry()
  
	def allow_deduction_only_for_single_party(self):
		if self.deduct:
			if len(self.item) > 1:
				frappe.throw("Deduction will be allowed only with single Party")	

	def validate_data(self):
		tds_amt = gross_amt = net_amt = taxable_amt = deduction_amt = 0.00
		if self.deduct:
			for d in self.deduct:
				deduction_amt += flt(d.amount)
			self.deduction_amount = flt(deduction_amt)
		else:
			self.deduction_amount = 0.00
    
		if not self.single_party_multiple_payments:
			for a in self.item:
				if self.payment_type == "Receive":
					inter_company = frappe.db.get_value("Customer", self.party, "inter_company")
					if inter_company == 0:
						frappe.throw(_("Selected Customer {0} is not inter company ".format(self.party)))
      
				if self.tds_percent and self.tds_percent > 0:
					a.tds_amount = flt(a.taxable_amount) * flt(self.tds_percent) / 100
				else:
					a.tds_amount = 0.00

				a.net_amount = flt(a.amount) - flt(a.tds_amount)
				tds_amt += flt(a.tds_amount)
				gross_amt += flt(a.amount)
				net_amt += flt(a.net_amount)
				taxable_amt += flt(a.taxable_amount)
		else:
			for a in self.multiple_account:
				gross_amt += flt(a.amount)
				
			taxable_amt = gross_amt
		
			if self.tds_percent:
				tds_amt = flt(self.tds_percent) * flt(taxable_amt) / 100

			net_amt = flt(gross_amt) - flt(tds_amt)

		self.tds_amount = tds_amt
		self.gross_amount = gross_amt
		self.amount = gross_amt
		self.net_amount = flt(net_amt) - flt(deduction_amt)
		self.taxable_amount = taxable_amt
		
	##
	# Update the Committedd Budget for checking budget availability
	##
	def consume_budget(self):
		if self.payment_type == "Payment":
			if not self.single_party_multiple_payments:
				bud_obj = frappe.get_doc({
						"doctype": "Committed Budget",
						"account": self.debit_account,
						"cost_center": self.cost_center,
						"po_no": self.name,
						"po_date": self.posting_date,
						"amount": self.amount,
						"poi_name": self.name,
						"date": frappe.utils.nowdate()
						})
				bud_obj.flags.ignore_permissions = 1
				bud_obj.submit()

				consume = frappe.get_doc({
						"doctype": "Consumed Budget",
						"account": self.debit_account,
						"cost_center": self.cost_center,
						"po_no": self.name,
						"po_date": self.posting_date,
						"amount": self.amount,
						"pii_name": self.name,
						"com_ref": bud_obj.name,
						"date": frappe.utils.nowdate()})
				consume.flags.ignore_permissions=1
				consume.submit()
			else:
				for a in self.multiple_account:
					bud_obj = frappe.get_doc({
						"doctype": "Committed Budget",
						"account": a.debit_account,
						"cost_center": self.cost_center,
						"po_no": self.name,
						"po_date": self.posting_date,
						"amount": a.amount,
						"poi_name": self.name,
						"date": frappe.utils.nowdate()
						})
					bud_obj.flags.ignore_permissions = 1
					bud_obj.submit()

					consume = frappe.get_doc({
							"doctype": "Consumed Budget",
							"account": a.debit_account,
							"cost_center": self.cost_center,
							"po_no": self.name,
							"po_date": self.posting_date,
							"amount": a.amount,
							"pii_name": self.name,
							"com_ref": bud_obj.name,
							"date": frappe.utils.nowdate()})
					consume.flags.ignore_permissions=1
					consume.submit()
										
	##
	# Cancel budget check entry
	##
	def cancel_budget_entry(self):
		frappe.db.sql("delete from `tabCommitted Budget` where po_no = %s", self.name)
		frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name)

	def post_gl_entry(self):
		gl_entries      = []
		total_amount    = 0.0
		total_amt = flt(self.net_amount + self.tds_amount + self.deduction_amount)
		if round(total_amt,2) == round(self.amount,2):
			if self.payment_type == "Receive":
				for a in self.item:
					account_type = frappe.db.get_value("Account", self.debit_account, "account_type") or ""
					party = party_type = None
					if account_type in ["Receivable", "Payable"]:
						party = a.party
						party_type = a.party_type
					gl_entries.append(
						self.get_gl_dict({
							"account": self.debit_account,
							"debit": a.net_amount,
							"debit_in_account_currency": a.net_amount,
							"voucher_no": self.name,
							"voucher_type": self.doctype,
							"cost_center": self.cost_center,
							'party': party,
							'party_type': party_type,						
							"company": self.company,
							"remarks": self.remarks
							})
						)
					
					account_type = frappe.db.get_value("Account", self.credit_account, "account_type") or ""
					party = party_type = None
					if account_type in ["Receivable", "Payable"]:
						party = a.party
						party_type = a.party_type
					gl_entries.append(
						self.get_gl_dict({
							"account": self.credit_account,
							"credit": a.amount,
							"credit_in_account_currency": a.amount,
							"voucher_no": self.name,
							"voucher_type": self.doctype,
							"cost_center": self.cost_center,
							'party': party,
							'party_type': party_type,	
							"company": self.company,
							"remarks": self.remarks
							})
						)
     
				if flt(self.tds_amount) > 0:
					gl_entries.append(
						self.get_gl_dict({
							"account": self.tds_account,
							"debit": self.tds_amount,
							"debit_in_account_currency": self.tds_amount,
							"voucher_no": self.name,
							"voucher_type": self.doctype,
							"cost_center": self.cost_center,
							"company": self.company,
							"remarks": self.remarks,
							})
						)

			else:
				if not self.single_party_multiple_payments:
					credit_account_type = frappe.db.get_value("Account", self.credit_account, "account_type") or ""
					debit_account_type = frappe.db.get_value("Account", self.debit_account, "account_type") or ""
					if len(self.item) == 1:
						party = party_type = None
						if debit_account_type in ["Receivable", "Payable"]:
							for b in self.item:
								party = b.party
								party_type = b.party_type
						gl_entries.append(
							self.get_gl_dict({
								"account": self.debit_account,
								"debit": self.amount,
								"debit_in_account_currency": self.amount,
								"voucher_no": self.name,
								"voucher_type": self.doctype,
								"cost_center": self.cost_center,
								'party': party,
								'party_type': party_type,						
								"company": self.company,
								"remarks": self.remarks
								})
							)

						party = party_type = None
						if credit_account_type in ["Receivable", "Payable"]:
							for b in self.item:
								party = b.party
								party_type = b.party_type
						gl_entries.append(
							self.get_gl_dict({
								"account": self.credit_account,
								"credit": self.net_amount,
								"credit_in_account_currency": self.net_amount,
								"voucher_no": self.name,
								"voucher_type": self.doctype,
								"cost_center": self.cost_center,
								'party': party,
								'party_type': party_type,
								"company": self.company,
								"remarks": self.remarks
								})
							)
					else:
						for a in self.item:
							party = party_type = None
							if debit_account_type in ["Receivable", "Payable"]:
								party = a.party
								party_type = a.party_type
							gl_entries.append(
								self.get_gl_dict({
									"account": self.debit_account,
									"debit": a.amount,
									"debit_in_account_currency": a.amount,
									"voucher_no": self.name,
									"voucher_type": self.doctype,
									"cost_center": self.cost_center,
									'party': party,
									'party_type': party_type,						
									"company": self.company,
									"remarks": self.remarks
									})
								)

							party = party_type = None
							if credit_account_type in ["Receivable", "Payable"]:
								party = a.party
								party_type = a.party_type
							gl_entries.append(
								self.get_gl_dict({
									"account": self.credit_account,
									"credit": a.net_amount,
									"credit_in_account_currency": a.net_amount,
									"voucher_no": self.name,
									"voucher_type": self.doctype,
									"cost_center": self.cost_center,
									'party': party,
									'party_type': party_type,
									"company": self.company,
									"remarks": self.remarks
									})
								)
				else:
					credit_account_type = frappe.db.get_value("Account", self.credit_account, "account_type") or ""
					for a in self.multiple_account:
						debit_account_type = frappe.db.get_value("Account", a.debit_account, "account_type") or ""
						party = party_type = None
						if debit_account_type in ["Receivable", "Payable"]:
							party = self.party
							party_type = "Supplier"

						gl_entries.append(
							self.get_gl_dict({
								"account": a.debit_account,
								"debit": a.amount,
								"debit_in_account_currency": a.amount,
								"voucher_no": self.name,
								"voucher_type": self.doctype,
								"cost_center": self.cost_center,
								'party': party,
								'party_type': party_type,		
								"company": self.company,
								"remarks": self.remarks,
								})
							)
					party = party_type = None	
					if credit_account_type in ["Receivable", "Payable"]:
						party = self.party
						party_type = "Supplier"

					gl_entries.append(
						self.get_gl_dict({
							"account": self.credit_account,
							"credit": self.net_amount,
							"credit_in_account_currency": self.net_amount,
							"voucher_no": self.name,
							"voucher_type": self.doctype,
							"cost_center": self.cost_center,
							'party': party,
							'party_type': party_type,
							"company": self.company,
							"remarks": self.remarks
							})
						)
				if flt(self.tds_amount) > 0:
					gl_entries.append(
						self.get_gl_dict({
							"account": self.tds_account,
							"credit": self.tds_amount,
							"credit_in_account_currency": self.tds_amount,
							"voucher_no": self.name,
							"voucher_type": self.doctype,
							"cost_center": self.cost_center,
							"company": self.company,
							"remarks": self.remarks
							})
						)
     
			if self.deduct:
				for a in self.deduct:
					debit_account_type = frappe.db.get_value("Account", a.account, "account_type") or ""
					party = party_type = None
					if debit_account_type in ["Receivable", "Payable"]:
						party = a.party
						party_type = a.party_type
					gl_entries.append(
							self.get_gl_dict({
								"account": a.account,
								"credit": a.amount,
								"credit_in_account_currency": a.amount,
								"voucher_no": self.name,
								"voucher_type": self.doctype,
								"cost_center": self.cost_center,
        						"party": party,
								"party_type": party_type,
								"company": self.company,
								"remarks": self.remarks
								})
							)
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)
		else:
			frappe.throw("Total Debit is not equal to Total Credit. It has to be equal")

@frappe.whitelist()
def get_tds_account(percent, payment_type):
	if payment_type == "Payment":
		if percent:
			if cint(percent) == 2:
				field = "tds_2_account"		
			elif cint(percent) == 3:
				field = "tds_3_account"		
			elif cint(percent) == 5:
				field = "tds_5_account"		
			elif cint(percent) == 10:
				field = "tds_10_account"		
			else:
				frappe.throw("Set TDS Accounts in Accounts Settings and try again")
			return frappe.db.get_single_value("Accounts Settings", field)
				
	elif payment_type == "Receive":
		if percent:
			field = "tds_deducted"
			return frappe.db.get_single_value("Accounts Settings", field)
