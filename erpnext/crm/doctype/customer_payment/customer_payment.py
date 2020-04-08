# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt, now
from frappe.model.document import Document
from frappe.core.doctype.user.user import send_sms

class CustomerPayment(Document):
	def validate(self):
		self.validate_defaults()
		self.get_customer_order()
		self.validate_amount()

	def after_insert(self):
		doc = frappe.get_doc("Site Type", frappe.db.get_value("Site", self.site, "site_type"))
		credit_allowed = frappe.db.get_value("Mode of Payment", self.mode_of_payment, "credit_allowed")
		if cint(doc.credit_allowed) and cint(credit_allowed):
			msg = "You Credit Request is placed successfully. You will be notified upon approval by NRDCL. Tran Ref No {0}".format(self.name)
			self.sendsms(msg)

	def on_submit(self):
		''' create sales order and payment entry '''
		if self.approval_status == "Rejected":
			return
		elif self.approval_status == "Pending":
			frappe.throw(_("Request cannot be submitted in <b>Pending</b> status"))

		self.make_sales_order()
		doc = frappe.get_doc("Site Type", frappe.db.get_value("Site", self.site, "site_type"))
		credit_allowed = frappe.db.get_value("Mode of Payment", self.mode_of_payment, "credit_allowed")
		if cint(doc.credit_allowed) and cint(credit_allowed):
			self.validate_documents()
		else:
			self.make_payment_entry()
			self.update_balance_amount()

	def before_cancel(self):
		self.update_balance_amount()

	def sendsms(self,msg=None):
		mobile_no = frappe.db.get_value("User", self.user, "mobile_no")
		if mobile_no:
			send_sms(mobile_no, msg)

	def validate_documents(self):
		''' document attachment is mandatory for credit '''
		if not frappe.db.exists('File', {'attached_to_doctype': self.doctype, 'attached_to_name': self.name}):
			frappe.throw(_("Please attach supporting document for Credit Request"))

	def update_balance_amount(self):
		paid_amount = flt(self.paid_amount) * (-1 if self.docstatus == 2 else 1)
		doc = frappe.get_doc("Customer Order", self.customer_order)
		doc.total_paid_amount += flt(paid_amount)
		doc.total_balance_amount += -1*flt(paid_amount)
		doc.save(ignore_permissions=True)

	def make_sales_order(self):
		if not frappe.db.exists("Sales Order", {"customer_order": self.customer_order, "docstatus": 1}):
			doc = frappe.get_doc("Customer Order", self.customer_order)
			if doc.docstatus == 0:
				doc.submit()
			else:
				doc.run_method("make_sales_order")

	def make_payment_entry(self):
		frappe.flags.ignore_account_permission = True
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_party_details
		from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account

		default_company = frappe.db.get_single_value('Global Defaults', 'default_company')
		cost_center 	= frappe.db.get_value("Branch", self.branch, "cost_center")
		party_details 	= get_party_details(default_company, "Customer", self.customer, now())
		paid_to 	= get_bank_cash_account(self.mode_of_payment, default_company)	
		sales_order 	= frappe.db.get_value("Customer Order", self.customer_order, "sales_order")
		if flt(self.paid_amount) > flt(self.total_balance_amount):
			allocated_amount = flt(self.total_balance_amount)
		else:
			allocated_amount = flt(self.paid_amount)
		doc = frappe.get_doc({
			"doctype": "Payment Entry",
			"branch": self.branch,
			"site": self.site,
			"customer_order": self.customer_order,
			"customer_payment": self.name,
			"naming_series": "Journal Entry",
			"payment_type": "Receive",
			"party_type": "Customer",
			"party": self.customer,
			"paid_from": party_details['party_account'],
			"paid_from_account_currency": party_details['party_account_currency'],
			"paid_from_account_balance": flt(party_details['account_balance']),
			"party_balance": flt(party_details['party_balance']),
			"mode_of_payment": self.mode_of_payment,
			"pl_cost_center": cost_center,
			"paid_to": self.paid_to if self.mode_of_payment.lower() == "cheque payment" else paid_to['account'],
			"paid_amount": flt(self.paid_amount), 
			"actual_receivable_amount": flt(self.paid_amount),
			"received_amount": flt(self.paid_amount),
			"reference_no": self.reference_no if self.mode_of_payment.lower() == "cheque payment" else None,
			"reference_date": self.reference_date if self.mode_of_payment.lower() == "cheque payment" else None,
			"references": [{
				"reference_doctype": "Sales Order",
				"reference_name": sales_order,
				"outstanding_amount": self.total_balance_amount,
				"allocated_amount": allocated_amount
			}]
		})
		doc.save(ignore_permissions=True)
		doc.submit()	
		self.db_set("sales_order", sales_order)
		self.db_set("payment_entry", doc.name)

	def validate_defaults(self):
		if not self.customer_order:
			frappe.throw(_("Please select an Order first"))
		elif str(self.mode_of_payment).lower() == "cheque payment":
			if not self.reference_no:
				frappe.throw(_("Please enter valid Cheque Number"))
			if not self.reference_date:
				frappe.throw(_("Please enter valid Cheque Date"))
			if not self.paid_to:
				frappe.throw(_("Account Paid To is mandatory"))

		if self.approval_status == "Rejected" and not self.rejection_reason:
			frappe.throw(_("Rejection Reason cannot be empty"))

	def get_customer_order(self):
		doc = frappe.get_doc("Customer Order", self.customer_order)
		self.user 	= doc.user
		self.site 	= doc.site
		self.branch	= doc.branch
		self.customer	= doc.customer
		self.sales_order= doc.sales_order
		self.total_payable_amount = flt(doc.total_payable_amount)
		self.total_paid_amount	  = flt(doc.total_paid_amount)
		self.total_balance_amount = flt(doc.total_balance_amount)

	def validate_amount(self):
		doc = frappe.get_doc("Site Type", frappe.db.get_value("Site", self.site, "site_type"))
		credit_allowed = frappe.db.get_value("Mode of Payment", self.mode_of_payment, "credit_allowed")
		if cint(doc.credit_allowed) and cint(credit_allowed):
			self.paid_amount = flt(self.total_balance_amount)
		elif not cint(doc.credit_allowed) and cint(credit_allowed):
			frappe.throw(_("Credit payment not permitted for sites of type {0}").format(doc.name))
		else:
			if str(self.mode_of_payment).lower() == "online payment":
				if not self.online_payment:
					frappe.throw(_("Online Payment entry not found"))	
			else:
				if cint(doc.payment_required):
					min_payment_required = flt(doc.min_payment_flat) if doc.payment_type == "Flat" \
							else flt(self.total_payable_amount)*flt(doc.min_payment_percent)*0.01 
					if flt(self.paid_amount) <= 0:
						frappe.throw(_("Payment amount must be greater zero"))
					if not flt(self.total_paid_amount) and flt(self.paid_amount,2) < flt(min_payment_required,2):
						if not frappe.db.exists("Customer Payment", {"customer_order": self.customer_order, "docstatus": 1}):
							frappe.throw(_("You need to make minimum payment of Nu. {0}/-").format('{:,.2f}'.format(min_payment_required)))
		if flt(self.paid_amount) > flt(self.total_balance_amount):
			frappe.throw(_("Paid amount cannot be more than balance payable amount"))

	def submit_customer_payment(self, doc):
		#doc.flags.ignore_permissions=True
		doc.save(ignore_permissions=True)
		doc.submit()
