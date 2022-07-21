# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		                    08/08/2016         DocumentNaming standard is introduced
1.0               SHIV                              15/08/2016         Introducing Loss Tolerance for Sales
1.0               SHIV                              22/09/2016         get_default_bank_cash_sales_account is introduced.
2.0               SHIV                              03/01/2018         *Following fields introduced
                                                                        party_currency, party_exchange_rate, party_paid_amount
2.0               SHIV                              31/07/2018         Fields party_type, party added under deductions
3.0               SHIV                              30/10/2018         Fetching cost_center from Branch master unlike cdcl.
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''
from __future__ import unicode_literals
import frappe, json
from frappe import _, scrub, ValidationError
from frappe.utils import flt, comma_or, nowdate, getdate, get_datetime
from erpnext.accounts.utils import get_outstanding_invoices, get_account_currency, get_balance_on
from erpnext.accounts.party import get_party_account
from erpnext.accounts.doctype.journal_entry.journal_entry \
	import get_average_exchange_rate, get_default_bank_cash_account, get_default_bank_cash_sales_account
from erpnext.setup.utils import get_exchange_rate
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.custom_utils import generate_receipt_no, check_future_date, get_branch_cc
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba
from frappe.model.mapper import get_mapped_doc

from erpnext.controllers.accounts_controller import AccountsController

# Ver 1.0 by SSK on 09/08/2016, Following datetime, make_autoname imports are included
import datetime
from frappe.model.naming import make_autoname
from erpnext.custom_autoname import get_auto_name
from frappe import msgprint

class InvalidPaymentEntry(ValidationError): pass

class PaymentEntry(AccountsController):
	def setup_party_account_field(self):		
		self.party_account_field = None
		self.party_account = None
		self.party_account_currency = None
		
		if self.payment_type == "Receive":
			self.party_account_field = "paid_from"
			self.party_account = self.paid_from
			self.party_account_currency = self.paid_from_account_currency
			
		elif self.payment_type == "Pay":
			self.party_account_field = "paid_to"
			self.party_account = self.paid_to
			self.party_account_currency = self.paid_to_account_currency

        # Ver 1.0 by SSK on 09/08/2016, autoname() method is added
	def autoname(self):
		self.name = make_autoname(get_auto_name(self, self.naming_series) + ".#####")

	def validate(self):
		check_future_date(self.posting_date)
		self.setup_party_account_field()
		self.set_missing_values()
		self.validate_payment_type()
		self.validate_party_details()
		self.validate_bank_accounts()
		self.set_exchange_rate()
		self.validate_mandatory()
		self.validate_reference_documents()
		self.set_amounts()
		self.clear_unallocated_reference_document_rows()
		self.validate_payment_against_negative_invoice()
		self.validate_transaction_reference()
		self.set_title()
		self.set_remarks()
		
	def on_submit(self):
		self.setup_party_account_field()
		if self.difference_amount:
			frappe.throw(_("Difference Amount must be zero"))
		self.make_gl_entries()
		self.update_advance_paid()
		if self.consolidated_invoice_id:
			ci = frappe.get_doc("Consolidated Invoice",self.consolidated_invoice_id)
			ci.db_set("payment_entry",self.name)
		
	def on_cancel(self):
		if self.clearance_date:
                        frappe.throw("Already done bank reconciliation.")

		self.setup_party_account_field()
		self.make_gl_entries(cancel=1)
		self.update_advance_paid()
							
	def set_missing_values(self):
		if not self.business_activity:
			self.business_activity = get_default_ba() 
		if self.payment_type == "Internal Transfer":
			for field in ("party", "party_balance", "total_allocated_amount", 
				"base_total_allocated_amount", "unallocated_amount"):
					self.set(field, None)
			self.references = []
		else:
			if not self.party_type:
				frappe.throw(_("Party Type is mandatory"))
				
			if not self.party:
				frappe.throw(_("Party is mandatory"))
		
		if self.party:
			if not self.party_balance:
				self.party_balance = get_balance_on(party_type=self.party_type,
					party=self.party, date=self.posting_date, company=self.company)
			
			if not self.party_account:
				party_account = get_party_account(self.party_type, self.party, self.company)
				self.set(self.party_account_field, party_account)
				self.party_account = party_account
				
		if self.paid_from and not (self.paid_from_account_currency or self.paid_from_account_balance):
			acc = get_account_details(self.paid_from, self.posting_date)
			self.paid_from_account_currency = acc.account_currency
			self.paid_from_account_balance = acc.account_balance
				
		if self.paid_to and not (self.paid_to_account_currency or self.paid_to_account_balance):
			acc = get_account_details(self.paid_to, self.posting_date)
			self.paid_to_account_currency = acc.account_currency
			self.paid_to_account_balance = acc.account_balance
			
		self.party_account_currency = self.paid_from_account_currency \
			if self.payment_type=="Receive" else self.paid_to_account_currency
			
		self.set_missing_ref_details()			
	
	def set_missing_ref_details(self):
		for d in self.get("references"):
			if d.allocated_amount:
				ref_details = get_reference_details(d.reference_doctype, 
					d.reference_name, self.party_account_currency)
					
				for field, value in ref_details.items():
					if not d.get(field):
						d.set(field, value)
						
	def validate_payment_type(self):
		if self.payment_type not in ("Receive", "Pay", "Internal Transfer"):
			frappe.throw(_("Payment Type must be one of Receive, Pay and Internal Transfer"))
	
	def validate_party_details(self):
		if self.party:
			if not frappe.db.exists(self.party_type, self.party):
				frappe.throw(_("Invalid {0}: {1}").format(self.party_type, self.party))
			
			if self.party_account:
				party_account_type = "Receivable" if self.party_type=="Customer" else "Payable"
				self.validate_account_type(self.party_account, [party_account_type])
					
	def validate_bank_accounts(self):
		if self.payment_type in ("Pay", "Internal Transfer"):
			self.validate_account_type(self.paid_from, ["Bank", "Cash"])
			
		if self.payment_type in ("Receive", "Internal Transfer"):
			self.validate_account_type(self.paid_to, ["Bank", "Cash"])
			
	def validate_account_type(self, account, account_types):
		account_type = frappe.db.get_value("Account", account, "account_type")
		if account_type not in account_types:
			frappe.throw(_("Account Type for {0} must be {1}").format(account, comma_or(account_types)))
				
	def set_exchange_rate(self):
		if self.paid_from and not self.source_exchange_rate:
			if self.paid_from_account_currency == self.company_currency:
				self.source_exchange_rate = 1
			elif self.payment_type in ("Pay", "Internal Transfer"):
				self.source_exchange_rate = get_average_exchange_rate(self.paid_from)
			else:
				self.source_exchange_rate = get_exchange_rate(self.paid_from_account_currency, 
					self.company_currency)
		
		if self.paid_to and not self.target_exchange_rate:
			self.target_exchange_rate = get_exchange_rate(self.paid_to_account_currency, 
				self.company_currency)
				
	def validate_mandatory(self):
		for field in ("paid_amount", "received_amount", "source_exchange_rate", "target_exchange_rate"):
			if not self.get(field):
				frappe.throw(_("{0} is mandatory").format(self.meta.get_label(field)))
				
	def validate_reference_documents(self):
		if self.party_type == "Customer":
			valid_reference_doctypes = ("Sales Order", "Sales Invoice", "Journal Entry")
		else:
			valid_reference_doctypes = ("Purchase Order", "Purchase Invoice", "Journal Entry")
			
		for d in self.get("references"):
			if not d.allocated_amount:
				continue
			if d.reference_doctype not in valid_reference_doctypes:
				frappe.throw(_("Reference Doctype must be one of {0}")
					.format(comma_or(valid_reference_doctypes)))
				
			elif d.reference_name:
				if not frappe.db.exists(d.reference_doctype, d.reference_name):
					frappe.throw(_("{0} {1} does not exist").format(d.reference_doctype, d.reference_name))
				else:
					ref_doc = frappe.get_doc(d.reference_doctype, d.reference_name)

					if d.reference_doctype != "Journal Entry":
						if self.party != ref_doc.get(scrub(self.party_type)):
							frappe.throw(_("{0} {1} does not associated with {2} {3}")
								.format(d.reference_doctype, d.reference_name, self.party_type, self.party))
					else:
						self.validate_journal_entry()
								
					if d.reference_doctype in ("Sales Invoice", "Purchase Invoice"):
						ref_party_account = ref_doc.debit_to \
							if self.party_type=="Customer" else ref_doc.credit_to
						if ref_party_account != self.party_account:
							frappe.throw(_("{0} {1} does not associated with Party Account {2}")
								.format(d.reference_doctype, d.reference_name, self.party_account))
						
					if ref_doc.docstatus != 1:
						frappe.throw(_("{0} {1} must be submitted")
							.format(d.reference_doctype, d.reference_name))
							
	def validate_journal_entry(self):
		for d in self.get("references"):
			if d.allocated_amount and d.reference_doctype == "Journal Entry":				
				je_accounts = frappe.db.sql("""select debit, credit from `tabJournal Entry Account`
					where account = %s and party=%s and docstatus = 1 and parent = %s
					and (reference_type is null or reference_type in ("", "Sales Order", "Purchase Order"))
					""", (self.party_account, self.party, d.reference_name), as_dict=True)

				if not je_accounts:
					frappe.throw(_("Row #{0}: Journal Entry {1} does not have account {2} or already matched against another voucher")
						.format(d.idx, d.reference_name, self.party_account))
				else:
					dr_or_cr = "debit" if self.payment_type == "Receive" else "credit"
					valid = False
					for jvd in je_accounts:
						if flt(jvd[dr_or_cr]) > 0:
							valid = True
					if not valid:
						frappe.throw(_("Against Journal Entry {0} does not have any unmatched {1} entry")
							.format(d.reference_name, dr_or_cr))
							
	def set_amounts(self):
		self.set_amounts_in_company_currency()
		self.set_total_allocated_amount()
		self.set_unallocated_amount()
		self.set_difference_amount()

	def set_amounts_in_company_currency(self):
		self.base_paid_amount, self.base_received_amount, self.difference_amount = 0, 0, 0
		if self.paid_amount:
			self.base_paid_amount = flt(flt(self.paid_amount) * flt(self.source_exchange_rate), 
				self.precision("base_paid_amount"))
				
		if self.received_amount:
			self.base_received_amount = flt(flt(self.received_amount) * flt(self.target_exchange_rate), 
				self.precision("base_received_amount"))
				
	def set_total_allocated_amount(self):
		if self.payment_type == "Internal Transfer":
			return
			
		total_allocated_amount, base_total_allocated_amount = 0, 0
		for d in self.get("references"):
			if d.allocated_amount:				
				total_allocated_amount += flt(d.allocated_amount)
				base_total_allocated_amount += flt(flt(d.allocated_amount) * flt(d.exchange_rate), 
					self.precision("base_paid_amount"))
					
		self.total_allocated_amount = abs(total_allocated_amount)
		self.base_total_allocated_amount = abs(base_total_allocated_amount)
	
	def set_unallocated_amount(self):
		self.unallocated_amount = 0;
		if self.party:
			party_amount = self.paid_amount if self.payment_type=="Receive" else self.received_amount
			
			total_deductions = sum([flt(d.amount) for d in self.get("deductions")])


                        # Ver 1.0 Begins added by SSK on 15/08/2016
                        # Following code is commented
			'''
			if self.total_allocated_amount < party_amount:
				if self.payment_type == "Receive":
					self.unallocated_amount = party_amount - (self.total_allocated_amount - total_deductions)
				else:
					self.unallocated_amount = party_amount - (self.total_allocated_amount + total_deductions)
			'''
			# Following line is added
			self.unallocated_amount = 0
			# Ver 1.0 Ends
				
	def set_difference_amount(self):
		base_unallocated_amount = flt(self.unallocated_amount) * (flt(self.source_exchange_rate) 
			if self.payment_type=="Receive" else flt(self.target_exchange_rate))
			
		base_party_amount = flt(self.base_total_allocated_amount) + flt(base_unallocated_amount)

                # Ver 1.0 Begins added SSK on 15/08/2016
                # Following code is commented
		'''
		if self.payment_type == "Receive":
			self.difference_amount = base_party_amount - self.base_received_amount
		elif self.payment_type == "Pay":
			self.difference_amount = self.base_paid_amount - base_party_amount
		else:
			self.difference_amount = self.base_paid_amount - flt(self.base_received_amount)
                '''
		# Following line is added
		if self.payment_type == "Receive":
                        self.difference_amount = self.total_allocated_amount - self.paid_amount
                else:
                        self.difference_amount = self.paid_amount - self.total_allocated_amount
		# Ver 1.0 Ends
		
		#for d in self.get("deductions"):
		#	if d.amount:
		#		self.difference_amount -= flt(d.amount)
				
		self.difference_amount = flt(self.difference_amount, self.precision("difference_amount"))
				
	def clear_unallocated_reference_document_rows(self):
		self.set("references", self.get("references", {"allocated_amount": ["not in", [0, None, ""]]}))

		frappe.db.sql("""delete from `tabPayment Entry Reference` 
			where parent = %s and allocated_amount = 0""", self.name)
			
	def validate_payment_against_negative_invoice(self):
		if ((self.payment_type=="Pay" and self.party_type=="Customer") 
				or (self.payment_type=="Receive" and self.party_type=="Supplier")):
				
			total_negative_outstanding = sum([abs(flt(d.outstanding_amount)) 
				for d in self.get("references") if flt(d.outstanding_amount) < 0])
			
			party_amount = self.paid_amount if self.payment_type=="Receive" else self.received_amount

			if not total_negative_outstanding:
				frappe.throw(_("Cannot {0} {1} {2} without any negative outstanding invoice")
					.format(self.payment_type, ("to" if self.party_type=="Customer" else "from"), 
						self.party_type), InvalidPaymentEntry)
					
			elif party_amount > total_negative_outstanding:
				frappe.throw(_("Paid Amount cannot be greater than total negative outstanding amount {0}")
					.format(total_negative_outstanding), InvalidPaymentEntry)
			
	def set_title(self):
		if self.payment_type in ("Receive", "Pay"):
			self.title = self.party
		else:
			self.title = self.paid_from + " - " + self.paid_to
			
	def validate_transaction_reference(self):
		bank_account = self.paid_to if self.payment_type == "Receive" else self.paid_from
		bank_account_type = frappe.db.get_value("Account", bank_account, "account_type")
		
		#if bank_account_type == "Bank":
			#if not self.reference_no or not self.reference_date:
				#frappe.throw(_("Reference No and Reference Date is mandatory for Bank transaction"))
				
	def set_remarks(self):
		if self.remarks: return
		
		if self.payment_type=="Internal Transfer":
			remarks = [_("Amount {0} {1} transferred from {2} to {3}")
				.format(self.paid_from_account_currency, self.paid_amount, self.paid_from, self.paid_to)]
		else:
			
			remarks = [_("Amount {0} {1} {2} {3}").format(
				self.party_account_currency,
				self.paid_amount if self.payment_type=="Receive" else self.received_amount,
				_("received from") if self.payment_type=="Receive" else _("to"), self.party
			)]
			
		if self.reference_no:
			remarks.append(_("Transaction reference no {0} dated {1}")
				.format(self.reference_no, self.reference_date))

		if self.payment_type in ["Receive", "Pay"]:
			for d in self.get("references"):
				if d.allocated_amount:
					remarks.append(_("Amount {0} {1} against {2} {3}").format(self.party_account_currency, 
						d.allocated_amount, d.reference_doctype, d.reference_name))
		
		for d in self.get("deductions"):
			if d.amount:
				remarks.append(_("Amount {0} {1} deducted against {2}")
					.format(self.company_currency, d.amount, d.account))

		self.set("remarks", "\n".join(remarks))
			
	def make_gl_entries(self, cancel=0, adv_adj=0):
		if self.payment_type in ("Receive", "Pay") and not self.get("party_account_field"):
			self.setup_party_account_field()
			
		gl_entries = []
		self.add_party_gl_entries(gl_entries)
		self.add_bank_gl_entries(gl_entries)
		self.add_tds_gl_entries(gl_entries)
		self.add_deductions_gl_entries(gl_entries)
		make_gl_entries(gl_entries, cancel=cancel, adv_adj=adv_adj)

	def add_party_gl_entries(self, gl_entries):
		if self.party_account:
			if self.payment_type=="Receive":
				against_account = self.paid_to
			else:
				 against_account = self.paid_from
			
				
			party_gl_dict = self.get_gl_dict({
				"account": self.party_account,
				"party_type": self.party_type,
				"party": self.party,
				"against": against_account,
				"cost_center": self.pl_cost_center,
				"business_activity": self.business_activity,
				"account_currency": self.party_account_currency
			})
			
			dr_or_cr = "credit" if self.party_type == "Customer" else "debit"
			
			for d in self.get("references"):
				inv = frappe.get_doc(d.reference_doctype, d.reference_name)
                                if self.payment_type == "Pay":
					if d.reference_doctype == "Purchase Invoice":
						cc  = inv.buying_cost_center
					else:
						cc  = self.pl_cost_center
                                else:
                                        # Ver 3.0 Begins, following line replaced by subsequent, by SHIV on 2018/10/30
                                        #cc  = frappe.db.get_value(doctype="Cost Center",filters={"branch": inv.branch},fieldname="name", as_dict=False)
                                        cc  = frappe.db.get_value(doctype="Branch",filters={"name": inv.branch},fieldname="cost_center", as_dict=False)
                                        # Ver 3.0 Ends
				gle = party_gl_dict.copy()
				gle.update({
					"against_voucher_type": d.reference_doctype,
					"against_voucher": d.reference_name,
					"business_activity": self.business_activity,
					"cost_center": cc
				})
				
				allocated_amount_in_company_currency = flt(flt(d.allocated_amount) * flt(d.exchange_rate), 
					self.precision("paid_amount"))	
				
				gle.update({
					dr_or_cr + "_in_account_currency": d.allocated_amount,
					dr_or_cr: allocated_amount_in_company_currency
				})
				gl_entries.append(gle)
				
			if self.unallocated_amount:
				base_unallocated_amount = base_unallocated_amount = self.unallocated_amount * \
					(self.source_exchange_rate if self.payment_type=="Receive" else self.target_exchange_rate)
					
				gle = party_gl_dict.copy()
				
				gle.update({
					dr_or_cr + "_in_account_currency": self.unallocated_amount,
					dr_or_cr: base_unallocated_amount
				})

				gl_entries.append(gle)
				
	def add_bank_gl_entries(self, gl_entries):
		total_deductions = 0
                for d in self.get("deductions"):
                        if d.amount:
                                total_deductions += flt(d.amount)

		if self.payment_type in ("Pay", "Internal Transfer"):
			if frappe.get_value("Account", self.paid_from, "report_type") == "Profit and Loss":	
				if self.pl_cost_center:
					gl_entries.append(
						self.get_gl_dict({
							"account": self.paid_from,
							"account_currency": self.paid_from_account_currency,
							"against": self.party if self.payment_type=="Pay" else self.paid_to,
							"credit_in_account_currency": self.paid_amount + total_deductions,
							"credit": self.base_paid_amount + total_deductions,
							"business_activity": self.business_activity,
							"cost_center": self.pl_cost_center
						})
					)
				else:
					frappe.throw("Please select a Cost Center under 'Cost Center (If Applicable)' field")
			else:
				gl_entries.append(
					self.get_gl_dict({
						"account": self.paid_from,
						"account_currency": self.paid_from_account_currency,
						"against": self.party if self.payment_type=="Pay" else self.paid_to,
						"credit_in_account_currency": self.paid_amount + total_deductions,
						"credit": self.base_paid_amount + total_deductions,
						"business_activity": self.business_activity,
						"cost_center": self.pl_cost_center
					})
				)

		if self.payment_type in ("Receive", "Internal Transfer"):
			if frappe.get_value("Account", self.paid_to, "report_type") == "Profit and Loss":	
				if self.pl_cost_center:
					gl_entries.append(
						self.get_gl_dict({
							"account": self.paid_to,
							"account_currency": self.paid_to_account_currency,
							"against": self.party if self.payment_type=="Receive" else self.paid_from,
							#"debit_in_account_currency": self.received_amount,
							#"debit": self.base_received_amount,
							"debit_in_account_currency": self.actual_receivable_amount - total_deductions,
							"debit": self.actual_receivable_amount - total_deductions,
							"business_activity": self.business_activity,
							"cost_center": self.pl_cost_center
						})
					)
				else:
					frappe.throw("Please select a Cost Center under 'Cost Center (If Applicable)' field")
			else:
				gl_entries.append(
					self.get_gl_dict({
						"account": self.paid_to,
						"account_currency": self.paid_to_account_currency,
						"against": self.party if self.payment_type=="Receive" else self.paid_from,
						#"debit_in_account_currency": self.received_amount,
						#"debit": self.base_received_amount
						"debit_in_account_currency": self.actual_receivable_amount - total_deductions,
						"debit": self.actual_receivable_amount - total_deductions,
						"business_activity": self.business_activity,
						"cost_center": self.pl_cost_center
					})
				)
			
	def add_deductions_gl_entries(self, gl_entries):
		for d in self.get("deductions"):
			if d.amount:
				account_currency = get_account_currency(d.account)
				if account_currency != self.company_currency:
					frappe.throw(_("Currency for {0} must be {1}").format(d.account, self.company_currency))

				dr_or_cr = "debit"
                                dr_or_cr_cur = "debit_in_account_currency"
                                if flt(d.amount) < 0:
                                        amount = -1 * flt(d.amount)
                                        dr_or_cr = "credit"
                                        dr_or_cr_cur = "credit_in_account_currency"
                                else:
                                        amount = flt(d.amount)
	
				account_type = frappe.db.get_value("Account", d.account, "account_type")

                                # ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
                                # Following code added by SHIV on 31/07/2018
				if account_type != "Payable" and account_type != "Receivable" and d.party:
                                        frappe.throw(_("Row#{0} : Party is not allowed against Non-payable or Non-receivable accounts.").format(d.idx), title="Invalid Data")
				# +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
				
				if account_type == "Payable" or account_type == "Receivable":
					gl_entries.append(
						self.get_gl_dict({
							"account": d.account,
							"account_currency": account_currency,
							"against": self.party or self.paid_from,
							dr_or_cr_cur: amount,
                                                        dr_or_cr: amount,
							"cost_center": d.cost_center,
							"business_activity": self.business_activity,
							"party_type": d.party_type,
							"party": d.party
						})
					)
				else:
					gl_entries.append(
						self.get_gl_dict({
							"account": d.account,
							"account_currency": account_currency,
							"against": self.party or self.paid_from,
							dr_or_cr_cur: amount,
                                                        dr_or_cr: amount,
							"business_activity": self.business_activity,
							"cost_center": d.cost_center
						})
					)
	
	def add_tds_gl_entries(self, gl_entries):
		if self.tds_amount:
			if self.pl_cost_center:
				if self.tds_account:
					gl_entries.append(
						self.get_gl_dict({
							"account": self.tds_account,
							"account_currency": self.paid_to_account_currency,
							"against": self.party if self.payment_type=="Receive" else self.paid_from,
							"debit_in_account_currency": self.tds_amount,
							"debit": self.tds_amount,
							"business_activity": self.business_activity,
							"cost_center": self.pl_cost_center,
							"party": self.party,
							"party_type": self.party_type
						})
					)
				else:
					frappe.throw("Please set TDS Account")
			else:
				frappe.throw("Please select a Cost Center under 'Cost Center (If Applicable)' field")
	
	def update_advance_paid(self):
		if self.payment_type in ("Receive", "Pay") and self.party:
			for d in self.get("references"):
				if d.allocated_amount and d.reference_doctype in ("Sales Order", "Purchase Order"):
					# if frappe.session.user == "Administrator":
					# 	frappe.throw(d.reference_name)
					#frappe.msgprint("the refernce docs {0} and {1} and {2}".format(d.allocated_amount, d.reference_doctype, d.reference_name))
					frappe.get_doc(d.reference_doctype, d.reference_name).set_total_advance_paid()

	def get_series(self):
		fiscal_year = getdate(self.posting_date).year
		generate_receipt_no(self.doctype, self.name, self.branch, fiscal_year)

@frappe.whitelist()
def get_outstanding_reference_documents(args):
	args = json.loads(args)

	party_account_currency = get_account_currency(args.get("party_account"))
	company_currency = frappe.db.get_value("Company", args.get("company"), "default_currency")
	
	# Get negative outstanding sales /purchase invoices
	total_field = "base_grand_total" if party_account_currency == company_currency else "grand_total"
		
	negative_outstanding_invoices = get_negative_outstanding_invoices(args.get("party_type"), 
		args.get("party"), args.get("party_account"), total_field)

	# Get positive outstanding sales /purchase invoices
	outstanding_invoices = get_outstanding_invoices(args.get("party_type"), args.get("party"), 
		args.get("party_account"))
	
	for d in outstanding_invoices:
		d["exchange_rate"] = 1
		if party_account_currency != company_currency \
			and d.voucher_type in ("Sales Invoice", "Purchase Invoice"):
				d["exchange_rate"] = frappe.db.get_value(d.voucher_type, d.voucher_no, "conversion_rate")

	# Get all SO / PO which are not fully billed or aginst which full advance not paid
	#orders_to_be_billed =  get_orders_to_be_billed(args.get("party_type"), args.get("party"), 
	#	party_account_currency, company_currency)
	
	return negative_outstanding_invoices + outstanding_invoices # + orders_to_be_billed
	
def get_orders_to_be_billed(party_type, party, party_account_currency, company_currency):
	voucher_type = 'Sales Order' if party_type == "Customer" else 'Purchase Order'

	ref_field = "base_grand_total" if party_account_currency == company_currency else "grand_total"

	orders = frappe.db.sql("""
		select
			name as voucher_no,
			{ref_field} as invoice_amount,
			({ref_field} - advance_paid) as outstanding_amount,
			transaction_date as posting_date
		from
			`tab{voucher_type}`
		where
			{party_type} = %s
			and docstatus = 1
			and ifnull(status, "") != "Closed"
			and {ref_field} > advance_paid
			and abs(100 - per_billed) > 0.01
		order by
			transaction_date, name
		""".format(**{
			"ref_field": ref_field,
			"voucher_type": voucher_type,
			"party_type": scrub(party_type)
		}), party, as_dict = True)

	order_list = []
	for d in orders:
		d["voucher_type"] = voucher_type
		d["exchange_rate"] = get_exchange_rate(party_account_currency, company_currency)
		order_list.append(d)

	return order_list
	
def get_negative_outstanding_invoices(party_type, party, party_account, total_field):
	voucher_type = "Sales Invoice" if party_type == "Customer" else "Purchase Invoice"
	return frappe.db.sql("""
		select
			"{voucher_type}" as voucher_type, name as voucher_no, 
			{total_field} as invoice_amount, outstanding_amount, posting_date, 
			due_date, conversion_rate as exchange_rate
		from
			`tab{voucher_type}`
		where
			{party_type} = %s and {party_account} = %s and docstatus = 1 and outstanding_amount < 0
		order by
			posting_date, name
		""".format(**{
			"total_field": total_field,
			"voucher_type": voucher_type,
			"party_type": scrub(party_type),
			"party_account": "debit_to" if party_type=="Customer" else "credit_to"
		}), (party, party_account), as_dict = True)
	
@frappe.whitelist()
def get_party_details(company, party_type, party, date):
	if not frappe.db.exists(party_type, party):
		frappe.throw(_("Invalid {0}: {1}").format(party_type, party))
		
	party_account = get_party_account(party_type, party, company)
	
	account_currency = get_account_currency(party_account)
	account_balance = get_balance_on(party_account, date)
	party_balance = get_balance_on(party_type=party_type, party=party)
	
	return {
		"party_account": party_account,
		"party_account_currency": account_currency,
		"party_balance": party_balance,
		"account_balance": account_balance
	}


@frappe.whitelist()
def get_account_details(account, date):
	''' Ver.3.0.191222 Begins, NRDCLCRM, CRMNRDCL, NRDCL CRM, CRM NRDCL '''
	# following line commented by SHIV on 2019/12/22
	#frappe.has_permission('Payment Entry', throw=True)
	# following code added by SHIV on 2019/12/22
	if "CRM Customer" not in frappe.get_roles():
		frappe.has_permission('Payment Entry', throw=True)
	''' Ver.3.0.19.12.22 Ends '''
	return frappe._dict({
		"account_currency": get_account_currency(account),
		"account_balance": get_balance_on(account, date),
		"account_type": frappe.db.get_value("Account", account, "account_type")
	})
	
@frappe.whitelist()
def get_company_defaults(company):
	fields = ["write_off_account", "exchange_gain_loss_account", "cost_center"]
	ret = frappe.db.get_value("Company", company, fields, as_dict=1)
	
	for fieldname in fields:
		if not ret[fieldname]:
			frappe.throw(_("Please set default {0} in Company {1}")
				.format(frappe.get_meta("Company").get_label(fieldname), company))
	
	return ret

@frappe.whitelist()
def get_reference_details(reference_doctype, reference_name, party_account_currency):
	total_amount = outstanding_amount = exchange_rate = None
	ref_doc = frappe.get_doc(reference_doctype, reference_name)
	
	if reference_doctype != "Journal Entry":
		if party_account_currency == ref_doc.company_currency:
			total_amount = ref_doc.base_grand_total
			exchange_rate = 1
		else:
			total_amount = ref_doc.grand_total
			exchange_rate = ref_doc.get("conversion_rate") or \
				get_exchange_rate(party_account_currency, ref_doc.company_currency)
		
		outstanding_amount = ref_doc.get("outstanding_amount") \
			if reference_doctype in ("Sales Invoice", "Purchase Invoice") \
			else flt(total_amount) - flt(ref_doc.advance_paid)			
	else:
		exchange_rate = get_exchange_rate(party_account_currency, ref_doc.company_currency)
		
	return frappe._dict({
		"due_date": ref_doc.get("due_date"),
		"total_amount": total_amount,
		"outstanding_amount": outstanding_amount,
		"exchange_rate": exchange_rate
	})
	
@frappe.whitelist()
def get_payment_entry(dt, dn, party_amount=None, bank_account=None, bank_amount=None):
	doc = frappe.get_doc(dt, dn)

	#for d in doc.get("items"):
        #        msgprint(d.item_code)

	# Ver 2.0 Begins, Following code added by SHIV on 03/01/2018
	party_currency = ''
	# Ver 2.0 Ends
	
	if dt in ("Sales Order", "Purchase Order") and flt(doc.per_billed, 2) > 0:
		frappe.throw(_("Can only make payment against unbilled {0}").format(dt))
	
	party_type = "Customer" if dt in ("Sales Invoice", "Sales Order") else "Supplier"

	# party account
	if dt == "Sales Invoice":
		so = frappe.db.sql("""select sales_order from `tabSales Invoice Item` where parent = '{0}'""".format(dn))[0][0]
		if so:
			is_credit = frappe.db.get_value("Sales Order", so, "is_credit")
			if is_credit == 1:
				frappe.throw("SI {} should be paid through Consolidated Sales Invoice".format(dn))
		else:
			frappe.throw("No Sales Order is linked with Sales Invoice {}".format(dn))
		party_account = doc.debit_to
	elif dt == "Purchase Invoice":
		party_account = doc.credit_to
	elif dt == "Purchase Order" and doc.status == "To Receive and Bill":
		party_account = frappe.db.get_single_value("Accounts Settings", "advance_to_supplier")
		if not party_account:
			frappe.throw("Setup Advance to Supplier Account in Accounts Settings")

		# Ver 2.0 Begins, Following code added by SHIV on 03/01/2018
		party_currency      = doc.get("currency")
		# Ver 2.0 Ends
	#### Added by Thukten Dendup ####		
	elif dt == "Sales Order":
		party_account = frappe.db.get_single_value("Accounts Settings", "advance_from_customer")
	#### End ######
	else:
		party_account = get_party_account(party_type, doc.get(party_type.lower()), doc.company)
		
	party_account_currency = doc.get("party_account_currency") or get_account_currency(party_account)
	
	# payment type
	if (dt == "Sales Order" or (dt=="Sales Invoice" and doc.outstanding_amount > 0)) \
		or (dt=="Purchase Invoice" and doc.outstanding_amount < 0):
			payment_type = "Receive"
	else:
		payment_type = "Pay"
	
	# amounts
	grand_total = outstanding_amount = 0
	if party_amount:
		grand_total = outstanding_amount = party_amount
	elif dt in ("Sales Invoice", "Purchase Invoice"):
		grand_total = doc.grand_total
		outstanding_amount = doc.outstanding_amount
	else:
		total_field = "base_grand_total" if party_account_currency == doc.company_currency else "grand_total"
		grand_total = flt(doc.get(total_field))
		outstanding_amount = grand_total - flt(doc.advance_paid)

	# bank or cash
	if dt =="Sales Invoice":
                bank = get_default_bank_cash_sales_account(doc.company, "Bank", mode_of_payment=doc.get("mode_of_payment"), 
                        account=bank_account)
	else:
                bank = get_default_bank_cash_account(doc.company, "Bank", mode_of_payment=doc.get("mode_of_payment"), 
                        account=bank_account)

	
	paid_amount = received_amount = 0
	if party_account_currency == bank.account_currency:
		paid_amount = received_amount = abs(outstanding_amount)
	elif payment_type == "Receive":
		paid_amount = abs(outstanding_amount)
		if bank_amount:
			received_amount = bank_amount
	else:
		received_amount = abs(outstanding_amount)
		if bank_amount:
			paid_amount = bank_amount

	ba = get_default_ba()
	cc = get_branch_cc(doc.branch)
	if dt == "Sales Invoice":
                bank_acc = frappe.db.get_value("Branch", doc.branch, "revenue_bank_account")
		ba = doc.business_activity
	elif dt == "Sales Order":
                bank_acc = frappe.db.get_value("Branch", doc.branch, "revenue_bank_account")
		ba = get_default_ba()
        elif dt == "Purchase Invoice":
                bank_acc = frappe.db.get_value("Branch", doc.branch, "expense_bank_account")
		ba = doc.business_activity
		cc = doc.buying_cost_center
        else:
                bank_acc = bank.account

	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = payment_type
	pe.company = doc.company
	pe.posting_date = nowdate()
	pe.mode_of_payment = doc.get("mode_of_payment")
	pe.party_type = party_type
	pe.party = doc.get(scrub(party_type))
	pe.paid_from = party_account if payment_type=="Receive" else bank_acc
	pe.paid_to = party_account if payment_type=="Pay" else bank_acc
	pe.paid_from_account_currency = party_account_currency \
		if payment_type=="Receive" else bank.account_currency
	pe.paid_to_account_currency = party_account_currency if payment_type=="Pay" else bank.account_currency
	pe.paid_amount = paid_amount
	pe.received_amount = received_amount
	pe.actual_receivable_amount = received_amount
	pe.branch = doc.branch	
	pe.business_activity = ba
	pe.pl_cost_center = cc

	if dt == "Sales Order" or dt == "Purchase Order":
		pe.so_reference = doc.name

        # Ver 2.0 Begins, Following code added SHIV on 03/01/2018
        if party_currency and bank.account_currency:
                pe.party_currency = party_currency
                party_exchange_rate = get_exchange_rate(party_currency, bank.account_currency)
                if party_exchange_rate:
                        pe.party_exchange_rate = party_exchange_rate
                        pe.party_paid_amount = (paid_amount / party_exchange_rate)
        # Ver 2.0 Ends

	pe.append("references", {
		"reference_doctype": dt,
		"reference_name": dn,
		"due_date": doc.get("due_date"),
		"total_amount": grand_total,
		"outstanding_amount": outstanding_amount,
		"allocated_amount": outstanding_amount
	})
	pe.setup_party_account_field()
	pe.set_missing_values()
	if party_account and bank:
		pe.set_exchange_rate()
		pe.set_amounts()
	return pe

# ePayment Begins
@frappe.whitelist()
def make_bank_payment(source_name, target_doc=None):
	def set_missing_values(obj, target, source_parent):
		target.payment_type = None
		target.transaction_type = "Payment Entry"
		target.posting_date = get_datetime()
		target.from_date = None
		target.to_date = None

	doc = get_mapped_doc("Payment Entry", source_name, {
	    "Payment Entry": {
		"doctype": "Bank Payment",
		"field_map": {
		    "name": "transaction_no",
		    "paid_from": "paid_from"
		},
		"postprocess": set_missing_values,
	    },
	}, target_doc, ignore_permissions=True)
	return doc
# ePayment Ends
