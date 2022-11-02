# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.accounts.doctype.imprest_receipt.imprest_receipt import get_opening_balance, update_dependencies
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.general_ledger import make_gl_entries

class ImprestRecoup(AccountsController):
	def validate(self):
		self.validate_defaults()
		self.update_defaults()
		self.update_amounts()
		self.validate_amounts()
		self.clearance_date = None

	def on_submit(self):
		for t in frappe.get_all("Imprest Recoup", ["name"], {"branch": self.branch, "imprest_type": self.imprest_type, "entry_date":("<",self.entry_date),"docstatus":0}):
			msg = '<b>Reference# : <a href="#Form/Imprest Recoup/{0}">{0}</a></b>'.format(t.name)
			frappe.throw(_("Found unclosed entries. Previous entries needs to be either closed or cancelled in order to determine opening balance for the current transaction.<br>{0}").format(msg),title="Invalid Operation")
		if not self.final_settlement:   # if condition added by SHIV on 2020/12/23 as per Ugyen Thinley's request, ticket#836
			self.post_receipt_entry()
		update_dependencies(self.branch, self.imprest_type, self.entry_date)
		self.post_gl_entry()
		self.consume_budget()
	
	def on_cancel(self):
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		
		if self.imprest_receipt:
			for t in frappe.get_all("Imprest Receipt", ["name"], {"name": self.imprest_receipt, "docstatus":1}):
				msg = '<b>Reference# : <a href="#Form/Imprest Receipt/{0}">{0}</a></b>'.format(t.name)
				frappe.throw(_("You need to cancel dependent Imprest Receipt entry first.<br>{0}").format(msg),title="Invalid Operation")
			
		self.post_gl_entry()
		update_dependencies(self.branch, self.imprest_type, self.entry_date)
		self.cancel_budget_entry()

	def validate_defaults(self):
		if frappe.db.get_value("Branch Imprest Item", {"parent": self.branch, "imprest_type": self.imprest_type}, "imprest_status") == "Closed":
			frappe.throw(_("Entries are not permitted for the closed imprest type <b>`{0}`</b>.").format(self.imprest_type), title="Imprest closed")
	
	def update_defaults(self):
		# Update entry_date
		#if not self.entry_date:
		if not self.get_db_value("entry_date"):
			self.entry_date = now_datetime()
		

		if self.docstatus == 0 and self.workflow_state == "Recouped":
			self.workflow_state = "Waiting Recoupment"

		#self.posting_date = nowdate() #Shiv 2019/01/02, Temporarily replaced with the following to enable backdating as requested by Dorji,BTL
		self.posting_date = nowdate() if not self.posting_date else self.posting_date

		# Update items
		self.purchase_amount = 0.0
		for i in self.items:
			i.amount = flt(i.quantity)*flt(i.rate)
			if flt(i.quantity) <= 0.0:
				frappe.throw(_("Row#{0} : Please input valid data for quantity.").format(i.idx),title="Invalid Quantity")
			elif flt(i.rate) <= 0.0:
				frappe.throw(_("Row#{0} : Please input valid data for rate.").format(i.idx),title="Invalid Rate")
			elif flt(i.amount) < 0.0:
				frappe.throw(_("Row#{0} : Amount cannot be a negative value.").format(i.idx),title="Invalid Amount")
			

			self.purchase_amount += flt(i.amount)
		self.purchase_amount = round(self.purchase_amount)
		
	def update_amounts(self):
		opening_balance = get_opening_balance(self.branch, self.imprest_type, self.name, self.entry_date)
		if flt(opening_balance) != flt(self.opening_balance):
			#frappe.msgprint(_("Opening balance has been changed from Nu.{0}/- to Nu.{1}/-").format(flt(self.opening_balance),flt(opening_balance)),title="Change in values")
			self.opening_balance = flt(opening_balance)

		self.closing_balance = flt(self.opening_balance)+flt(self.receipt_amount)-flt(self.purchase_amount)

	def validate_amounts(self):
		if flt(self.opening_balance) <= 0:
			frappe.throw("Insufficient Opening balance...",title="Insufficient Balance")
		elif flt(self.purchase_amount) < 0:
			frappe.throw("Purchase amount cannot be a negative value.",title="Invalid Data")
		elif not self.purchase_amount:
			frappe.throw("Purchase amount cannot be empty.",title="Invalid Data")
		elif flt(self.closing_balance) < 0:
			frappe.throw("Closing balance cannot be less than value zero.",title="Invalid Data")
			
		# Validate against imprest limit set under branch
		imprest_limit = frappe.db.get_value("Branch Imprest Item", {"parent": self.branch, "imprest_type": self.imprest_type}, "imprest_limit")

		if not imprest_limit:
			frappe.throw("Please set imprest limit for the branch.", title="Insufficient Balance")
		else:
			if flt(self.closing_balance) > flt(imprest_limit):
				frappe.throw(_("Closing balance cannot exceed imprest limit Nu.{0}/-.").format(flt(imprest_limit)),title="Invalid Data")

	def post_receipt_entry(self):
		if self.purchase_amount:
			doc = frappe.new_doc("Imprest Receipt")
			doc.update({
				"doctype": "Imprest Receipt",
				"company": self.company,
				"branch": self.branch,
				"title": "Recoupment for "+str(self.name),
				"entry_date": now_datetime(),
				"imprest_type": self.imprest_type,
				"amount": flt(self.purchase_amount,2),
				"revenue_bank_account": self.revenue_bank_account,
				"pay_to_recd_from": self.pay_to_recd_from,
				"select_cheque_lot": self.select_cheque_lot,
				"cheque_no": self.cheque_no,
				"cheque_date": self.cheque_date,
				"imprest_recoup": self.name,
				"workflow_state": "Approved"
			})
			doc.save(ignore_permissions = True)
			doc.submit()
			#self.imprest_receipt = doc.name
			self.db_set("imprest_receipt", doc.name)
		else:
			frappe.throw(_("Purchase amount cannot be empty."),title="Invalid Data")
	
	def post_gl_entry(self):
		gl_entries      = []
		entries         = {}
		accounts        = []
		total_amount    = 0.0
		account_type    = frappe.db.get_value("Account", self.settlement_account, "account_type") if not self.settlement_account_type else self.settlement_account_type
		#self.posting_date = nowdate()

		'''
		rev_gl = frappe.db.get_value(doctype="Branch",filters=self.branch,fieldname="revenue_bank_account", as_dict=True)
		if not rev_gl.revenue_bank_account:
			frappe.throw(_("Bank Account GL is not defined in Branch '{0}'.").format(self.branch),title="Data Not found")
		'''
		
		for i in self.items:
			total_amount += flt(i.amount)
			if not i.budget_account:
				frappe.throw(_("Row#{0} : Please select proper budget account.").format(i.idx),title="Missing Data")
				
			if entries.has_key(i.budget_account):
				entries[i.budget_account]['amount'] += flt(i.amount)
			else:
				entries[i.budget_account]  = {"type": "debit", "amount": flt(i.amount)}

		#entries[rev_gl.revenue_bank_account] = {"type": "credit", "amount": flt(total_amount)}
		if self.final_settlement:
			if not self.settlement_account:
				frappe.throw(_("Settlement Account cannot be blank for final settlement."), title="Missing Data")

			if account_type != "Payable" and account_type != "Receivable" and self.party:
				frappe.throw(_("Party is not allowed against Non-payable or Non-receivable accounts."), title="Invalid Data")

			if (account_type == "Payable" or account_type == "Receivable") and not self.party:
				frappe.throw(_("Party is mandatory."), title="Missing Data")

			entries[self.settlement_account] = {"type": "credit", "amount": flt(total_amount)}
		else:
			entries[self.revenue_bank_account] = {"type": "credit", "amount": flt(total_amount)}

		for gl in entries:
			gl_entries.append(
				self.get_gl_dict({
				       "account": gl,
				       "debit" if entries[gl]["type"] == "debit" else "credit": entries[gl]["amount"],
				       "debit_in_account_currency" if entries[gl]["type"] == "debit" else "credit_in_account_currency": entries[gl]["amount"],
				       "voucher_no": self.name,
				       "voucher_type": self.doctype,
				       "cost_center": self.cost_center,
				       "company": self.company,
				       "remarks": self.branch,
				       "against": self.party or self.pay_to_recd_from,
				       "party_type": self.party_type if self.final_settlement and entries[gl]["type"] == "credit" else "",
				       "party": self.party if self.final_settlement and entries[gl]["type"] == "credit" else ""
				})
			)
		
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
 	
	##
	# Update the Committedd Budget for checking budget availability
	##
	def consume_budget(self):
		for i in self.items:
			bud_obj = frappe.get_doc({
				"doctype": "Committed Budget",
				"account": i.budget_account,
				"cost_center": self.cost_center,
				"po_no": self.name,
				"po_date": self.posting_date,
				"amount": i.amount,
				"poi_name": self.name,
				"date": frappe.utils.nowdate()
				})
			bud_obj.flags.ignore_permissions = 1
			bud_obj.submit()

			consume = frappe.get_doc({
				"doctype": "Consumed Budget",
				"account": i.budget_account,
				"cost_center": self.cost_center,
				"po_no": self.name,
				"po_date": self.posting_date,
				"amount": i.amount,
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


	def post_journal_entry(self):
		entries         = {}
		accounts        = []
		total_amount    = 0.0
		
		# Fetching GLs
		rev_gl = frappe.db.get_value(doctype="Branch",filters=self.branch,fieldname="revenue_bank_account", as_dict=True)
		
		if not rev_gl.revenue_bank_account:
			frappe.throw(_("Bank Account GL is not defined in Branch '{0}'.").format(self.branch),title="Data Not found")

		for i in self.items:
			total_amount += flt(i.amount)
			if not i.budget_account:
				frappe.throw(_("Row#{0} : Please select proper budget account.").format(i.idx),title="Missing Data")
				
			if entries.has_key(i.budget_account):
				entries[i.budget_account]['amount'] += flt(i.amount)
			else:
				entries[i.budget_account]  = {"type": "debit", "amount": flt(i.amount)}

		entries[rev_gl.revenue_bank_account] = {"type": "credit", "amount": flt(total_amount)}
		
		for gl in entries:
			gl_det = frappe.db.get_value(doctype="Account", filters=gl, fieldname=["account_type","is_an_advance_account"], as_dict=True)                        
			accounts.append({"account": gl,
				 "debit_in_account_currency" if entries[gl]["type"]=="debit" else "credit_in_account_currency": flt(entries[gl]["amount"]),
				 "cost_center": self.cost_center,
				 "party_check": 0,
				 "account_type": gl_det.account_type,
				 "is_advance": "Yes" if gl_det.is_an_advance_account == 1 else None
			})

		je = frappe.new_doc("Journal Entry")
		
		je.update({
			"doctype": "Journal Entry",
			"voucher_type": "Bank Entry",
			"naming_series": "Bank Payment Voucher",
			"title": "Imprest Recoupment ("+str(self.name)+")",
			"user_remark": "Imprest Recoupment ("+str(self.name)+")",
			"posting_date": nowdate(),
			"company": self.company,
			"total_amount_in_words": money_in_words(total_amount),
			"accounts": accounts,
			"branch": self.branch,
			"imprest_recoup": self.name
		})
		je.save(ignore_permissions = True)
