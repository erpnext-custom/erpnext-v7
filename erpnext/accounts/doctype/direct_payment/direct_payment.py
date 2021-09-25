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
from frappe.model.mapper import get_mapped_doc

class DirectPayment(AccountsController):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_data()
		self.clearance_date = None

	def on_submit(self):
		self.post_gl_entry()
		self.consume_budget()

	def on_cancel(self):
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		self.post_gl_entry()
		self.cancel_budget_entry()

	def validate_data(self):
		tds_amt = gross_amt = net_amt = taxable_amt = 0.00
		if not self.single_party_multiple_payments:
			for a in self.item:
				if self.payment_type == "Receive":
					inter_company = frappe.db.get_value("Customer", self.party, "inter_company")
					if inter_company == 0:
						frappe.throw(_("Selected Customer {0} is not inter company ".format(self.party)))

				if self.payment_type == "Payment" and a.party_type == "Customer":
					frappe.throw(_("Party Type should be Supplier in Child table when Payment Type is Payment"))
				elif self.payment_type == "Receive" and a.party_type == "Supplier":
					frappe.throw(_("Party Type should be Customer in Child Table when Payment Type is Receive"))
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
		self.net_amount = net_amt
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
        # consolidation_party_type and consolidation_party this two field added for consolidation purpose
		gl_entries      = []
		total_amount    = 0.0
		total_amt = flt(self.net_amount + self.tds_amount)
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
							"remarks": self.remarks,
							"consolidation_party_type":a.party_type,
                        	"consolidation_party":a.party
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
							"remarks": self.remarks,
							"consolidation_party_type":a.party_type,
                        	"consolidation_party":a.party
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
								"remarks": self.remarks,
								"consolidation_party_type":a.party_type,
                        		"consolidation_party":a.party
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
								"remarks": self.remarks,
								"consolidation_party_type":a.party_type,
                        		"consolidation_party":a.party
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
								"consolidation_party_type":a.party_type,
                        		"consolidation_party":a.party
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

	

# ePayment Begins
@frappe.whitelist()
def make_bank_payment(source_name, target_doc=None):
	def set_missing_values(obj, target, source_parent):
		target.payment_type = None
		target.transaction_type = "Direct Payment"
		target.posting_date = get_datetime()
		target.from_date = None
		target.to_date = None
		bank_name, bank_branch, bank_account_no = frappe.db.get_value("Account", obj.credit_account, ['bank_name', 'bank_branch', 'bank_account_no'])
		target.bank_name = bank_name
		target.bank_branch = bank_branch
		target.bank_account_no = bank_account_no
		
	doc = get_mapped_doc("Direct Payment", source_name, {
			"Direct Payment": {
				"doctype": "Bank Payment",
				"field_map": {
					"name": "transaction_no",
					"credit_account": "paid_from",
			},
				"postprocess": set_missing_values,
			},
	}, target_doc, ignore_permissions=True)
	return doc
# ePayment Ends