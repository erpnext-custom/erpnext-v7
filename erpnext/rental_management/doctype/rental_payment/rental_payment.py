# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController

class RentalPayment(AccountsController):
	def validate(self):
		received_amt = 0
		if not self.individual_payment:
			self.tenant = ""
			self.tenant_name = ""

		for a in self.item:
			received_amt = received_amt + a.allocated_amount

		self.amount_received = received_amt
		if self.tds_amount:
			self.net_amount = self.amount_received - self.tds_amount
		else:
			self.net_amount = self.amount_received
	def on_submit(self):
		self.update_rental_bill()
		self.post_gl_entry()
	
	def on_cancel(self):
		self.flags.ignore_links = True
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		self.post_gl_entry()
		self.update_rental_bill()

	def update_rental_bill(self):
		if self.docstatus == 2:
			for a in self.item:
				total_received_amount = 0
				received_amount = frappe.db.get_value("Rental Bill", a.rental_bill, "received_amount")
				total_received_amount = received_amount - a.allocated_amount
				frappe.db.sql("Update `tabRental Bill` set received_amount = '{0}', rental_payment = '{1}' where name = '{2}'".format(total_received_amount, self.name, a.rental_bill))
				
		else:
			for a in self.item:
				total_received_amount = 0
				received_amount = frappe.db.get_value("Rental Bill", a.rental_bill, "received_amount")
				total_received_amount = received_amount + a.allocated_amount
				frappe.db.sql("Update `tabRental Bill` set received_amount = '{0}', rental_payment = '{1}' where name = '{2}'".format(total_received_amount, self.name, a.rental_bill))

	def post_gl_entry(self):
		gl_entries = []
		debit_account = frappe.db.get_single_value("Rental Account Setting", "revenue_claim_account")
		credit_account = self.credit_account
		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		business_activity = frappe.db.get_single_value("Rental Setting", "business_activity")
		#if self.individual_payment:
		#	party = frappe.db.get_value("Tenant Information", self.tenant, "customer_code")
		#	party_type = ""
		#else:
		#	party = ""
		#	party_type=""
		gl_entries.append(
			self.get_gl_dict({
			    "account": debit_account,
			    "debit": self.net_amount,
			    "debit_in_account_currency": self.net_amount,
			    "voucher_no": self.name,
			    "voucher_type": "Rental Payment",
			    "cost_center": cost_center,
		#	    'party': party,
		#	    'party_type': party_type,
			    "company": self.company,
			    "remarks": self.remarks,
			    "business_activity": business_activity
			})
		  )
		gl_entries.append(
			self.get_gl_dict({
				"account": credit_account,
				"credit": self.amount_received,
				"credit_in_account_currency": self.amount_received,
	        	       	"voucher_no": self.name,
		               	"voucher_type": "Rental Payment",
				"cost_center": cost_center,
				"company": self.company,
				"remarks": self.remarks,
				"business_activity": business_activity
			})
		    )

		if self.tds_amount > 0:
			gl_entries.append(
				self.get_gl_dict({
					"account": self.tds_account,
					"debit": self.tds_amount,
					"debit_in_account_currency": self.tds_amount,
					"voucher_no": self.name,
					"voucher_type": self.doctype,
					"cost_center": cost_center,
					"company": self.company,
					"remarks": self.remarks,
					"business_activity": business_activity
					})
				)

		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
		

	def get_rental_bill_list(self):
		condition = ""
		data = []
		if not self.individual_payment:
			if self.location:
				condition += " and location = '{0}'".format(self.location)
			if self.branch:
				condition += " and branch = '{0}'".format(self.branch)
			if self.building_category:
				condition += " and building_category = '{0}'".format(self.building_category)
			if self.ministry_agency:
				condition += " and ministry_agency = '{0}'".format(self.ministry_agency)
			if self.department:
				condition += " and department = '{0}'".format(self.department)
			if self.fiscal_year:
				condition += " and fiscal_year = '{0}'".format(self.fiscal_year)
			if self.month:
				condition += " and month = '{0}'".format(self.month)
			bill_lists = frappe.db.sql("""
			                         select name, tenant, tenant_name, customer_code, rent_amount, fiscal_year, month
                                                 from `tabRental Bill`
						 where 	docstatus = 1
		                                 and received_amount < rent_amount
			                         {0}
						 order by name	
					""".format(condition), as_dict=True)
		else:
			if self.tenant:
				condition += " and tenant = '{0}'".format(self.tenant)

			bill_lists = frappe.db.sql("""
			                         select name, tenant, tenant_name, customer_code, rent_amount, fiscal_year, month
                                                 from `tabRental Bill`
						 where 	docstatus = 1
		                                 and received_amount < rent_amount
			                         {0}
						 order by name	
					""".format(condition), as_dict=True)
                                                
		for a in bill_lists:
			 data.append({"bill_no":a.name, "tenant":a.tenant, "tenant_name":a.tenant_name, "customer_code":a.customer_code, "rent_amount":a.rent_amount, "fiscal_year":a.fiscal_year, "month":a.month})

		return data	

@frappe.whitelist()
def get_tds_account():
	return frappe.db.get_single_value("Accounts Settings", "tds_deducted")			
