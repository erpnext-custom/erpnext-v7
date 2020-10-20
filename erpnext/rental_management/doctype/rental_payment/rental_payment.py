# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, nowtime, getdate, nowdate, date_diff
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.utils.data import get_first_day, get_last_day, add_days

class RentalPayment(AccountsController):
	def validate(self):
		self.get_rental_bill()
		self.update_rental_official()
		self.generate_penalty()
		self.validate_records()

	def validate_records(self):	
		if not self.individual_payment:
			self.tenant = ""
			self.tenant_name = ""

		received_amt = 0
		for a in self.item:
			if a.amount_received < a.amount:
				a.allocated_amount = flt(a.amount_received)
			else:
				a.allocated_amount = flt(a.amount)
	
			received_amt += flt(a.amount_received)

		self.amount_received = flt(received_amt)
		if self.tds_amount > 0:
			self.net_amount = flt(self.amount_received) - flt(self.tds_amount)
		else:
			self.net_amount = flt(self.amount_received)
		if not self.write_off_penalty:
			self.net_amount = flt(self.amount_received) - flt(self.tds_amount) + flt(self.penalty_amount)
		

	def update_rental_official(self):
		if frappe.db.exists("Employee", {"user_id":frappe.session.user}):
			rental_official, rental_official_name = frappe.db.get_value("Employee", {"user_id":frappe.session.user}, ["employee", "employee_name"])
			if rental_official:
				self.rental_official = rental_official
				self.rental_official_name = rental_official_name

	def generate_penalty(self):
		if self.item and not self.write_off_penalty:
			total_penalty = 0.00
			for a in self.item:
				if not a.write_off_penalty:
					bill_date = frappe.db.get_value("Rental Bill", a.rental_bill, "posting_date")
					no_of_days = date_diff(self.posting_date, bill_date)
					examption_days = frappe.db.get_single_value("Rental Setting", "payment_due_on")
					penalty_rate = frappe.db.get_single_value("Rental Setting", "penalty_rate")
					if examption_days and penalty_rate:
						from datetime import datetime
						from dateutil import relativedelta
						start_penalty_from = add_days(bill_date, cint(examption_days))
						date1 = datetime.strptime(str(start_penalty_from), '%Y-%m-%d')
						date2 = datetime.strptime(str(self.posting_date), '%Y-%m-%d')
						months = (date2.year - date1.year) * 12 + (date2.month - date1.month)
						penalty_amt = 0.00
						if flt(no_of_days) > flt(examption_days):
							penalty_amt =  flt(penalty_rate)/100.00 * flt(months +1) * flt(a.amount)

						a.penalty = round(penalty_amt)
						total_penalty += a.penalty
					else:
						frappe.throw("Penalty Rate and Payment Due Date are missing in Rental Setting")

				else:
					a.penalty = 0.00
					
			self.penalty_amount = round(total_penalty)
		else:
			for a in self.item:
				a.write_off_penalty = 1
				a.penalty = 0.00

			self.penalty_amount = 0.00
	
	def get_rental_bill(self):
		amount_received = 0.00
		for i in self.item:
			if i.tenant and not i.rental_bill:
				data = self.get_rental_bill_list(i.tenant)
				if data:
					#frappe.msgprint(_("{}").format(data[0]['tenant_name']))
					i.tenant_name 	  = data[0]['tenant_name']
					i.cid   	  = data[0]['cid']
					i.customer_code   = data[0]['customer_code']
					i.rental_bill 	  = data[0]['bill_no']
					i.actual_rent_amount = data[0]['rent_amount']
					i.amount          = data[0]['receivable_amount']
					i.fiscal_year	  = data[0]['fiscal_year']
					i.month		  = data[0]['month']
					i.ministry_agency = data[0]['ministry_agency']
					i.department	  = data[0]['department']
					i.bulk_update	  = 1

			# add additional validations here
			if not i.amount_received:
				frappe.throw("Please set Reveived Amount for Row {}: Tenant ID: {}".format(i.idx, i.tenant))	
			
		self.amount_received = amount_received
		self.net_amount = flt(self.amount_received) - flt(self.tds_amount)
		# frappe.msgprint("{}, {}".format(self.amount_received, flt(amount_received)))

	def on_submit(self):
		self.update_rental_official()
		self.update_tenant_dept()
		self.update_rental_bill()
		self.post_gl_entry()
		self.update_advance_adjustment()
	
	def on_cancel(self):
		self.flags.ignore_links = True
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		self.post_gl_entry()
		self.update_rental_bill()
		self.update_advance_adjustment()
	
	def update_advance_adjustment(self):
		for a in self.item:
			if cint(a.amount_received) > cint(a.amount):
				if self.docstatus == 2:
					frappe.db.sql("delete from `tabRental Advance Received` where rental_bill = '{}'".format(a.rental_bill))	
				else:
					if frappe.db.exists("Rental Advance Adjustment", {"tenant": a.tenant}):
						raa_no = frappe.db.get_value("Rental Advance Adjustment", {"tenant": a.tenant}, "name")
						doc = frappe.get_doc("Rental Advance Adjustment", raa_no)
					else:
						doc = frappe.get_doc({
								"doctype": "Rental Advance Adjustment",
								"posting_date": nowdate,
								"tenant": a.tenant,
								"tenant_name": a.tenant_name,
							})
						
					doc.append('advance_received_item',{
							    'rental_bill': a.rental_bill,
							    'rent_amount': a.amount,
							    'received_amount': a.amount_received,
							    'balance_amount': flt(a.amount_received) - flt(a.amount),
							    'receipt_date': nowdate()
							})
					doc.save()

				raa_no1 = frappe.db.get_value("Rental Advance Adjustment", {"tenant": a.tenant}, "name")
				doc1 = frappe.get_doc("Rental Advance Adjustment", raa_no1)
				
				total_adjusted = 0.00
				total_receive = 0.00
				
				if doc1.advance_received_item:
					for b in doc1.advance_received_item:
						total_receive += flt(b.balance_amount)

				if doc1.advance_adjusted_item:
					for c in doc1.advance_adjusted_item:
						total_adjusted += flt(c.adjusted_amount)
				doc1.advance_received = total_receive
				doc1.advance_adjusted = total_adjusted
				doc1.advance_balance = flt(total_receive) - flt(total_adjusted)
				doc1.save()

	def update_rental_bill(self):
		if self.docstatus == 2:
			for a in self.item:
				doc = frappe.get_doc("Rental Bill", a.rental_bill)
				received_amount = flt(doc.received_amount) - flt(a.amount_received)
				frappe.db.sql("update `tabRental Bill` set `received_amount` = '{0}', `rental_payment` = '', balance_amount = 0.00  where name = '{1}'".format(received_amount, a.rental_bill))
		else:
			for a in self.item:
				doc = frappe.get_doc("Rental Bill", a.rental_bill)
				balance_amount = flt(a.amount_received) - flt(a.amount) if a.amount_received > a.amount else 0.00
				received_amount = flt(doc.received_amount) + flt(a.amount_received)
				frappe.db.sql("update `tabRental Bill` set `received_amount` = '{0}', `rental_payment` = '{1}', balance_amount = '{2}' where name = '{3}'".format(received_amount, self.name, balance_amount, a.rental_bill))
					
	def update_tenant_dept(self):
		for a in self.item:
			doc = frappe.get_doc("Tenant Information", a.tenant)
			flag = 0
			if a.ministry_agency != doc.ministry_agency:
				flag = 1
			if a.department != doc.department:
				flag = 1
			if flag:
				ti = frappe.get_doc("Tenant Information", a.tenant)
				if not ti.tenant_history:
					ti.append("tenant_history",{
							"department": ti.department,
							"ministry_agency": ti.ministry_agency,
							"floor_area": ti.floor_area,
							"from_date": ti.allocated_date,
							"to_date" : nowdate(),
							"creation": nowdate(),
							"modified_by": frappe.session.user,
							"modified": nowdate(),
							})
					ti.append("tenant_history",{
							"department": a.department,
							"ministry_agency": a.ministry_agency,
							"floor_area": ti.floor_area,
							"from_date": nowdate(),
							"creation": nowdate(),
							"modified_by": frappe.session.user,
							"modified": nowdate()
						      })

				else:
					ti.append("tenant_history",{
							"department": a.department,
							"ministry_agency": a.ministry_agency,
							"floor_area": ti.floor_area,
							"from_date": nowdate(),
							"creation": nowdate(),
							"modified_by": frappe.session.user,
							"modified": nowdate()
				})
				ti.save()
				# Update Tenant Information
				frappe.db.sql("update `tabTenant Information` set ministry_agency = '{0}', department = '{1}' where name ='{2}'".format(a.ministry_agency, a.department, a.tenant))
				# Update Rental Bill
				frappe.db.sql("update `tabRental Bill` set ministry_agency = '{0}', department = '{1}' where name ='{2}'".format(a.ministry_agency, a.department, a.rental_bill))
					

	def post_gl_entry(self):
		gl_entries = []
		credit_account = frappe.db.get_single_value("Rental Account Setting", "revenue_claim_account")
		debit_account = self.credit_account
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
		if self.penalty_amount > 0 and not self.write_off_penalty:
			penalty_acc = frappe.db.get_single_value("Rental Account Setting", "penalty_account")
			if not penalty_acc:
				frappe.throw("Penalty Account is not set in Rental Account Setting")

			gl_entries.append(
				self.get_gl_dict({
					"account": penalty_acc,
					"credit": self.penalty_amount,
					"credit_in_account_currency": self.penalty_amount,
					"voucher_no": self.name,
					"voucher_type": self.doctype,
					"cost_center": cost_center,
					"company": self.company,
					"remarks": self.remarks,
					"business_activity": business_activity
					})
				)

		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
		

	def get_rental_bill_list(self, tenant=None):
		condition = ""
		data = []
		if not self.individual_payment:
			if tenant:
				condition += " and tenant = '{}'".format(tenant)
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
			if self.dzongkhag:
				condition += " and dzongkhag = '{0}'".format(self.dzongkhag)
			bill_lists = frappe.db.sql("""
			                         select name, tenant, tenant_name, customer_code, cid, rent_amount, receivable_amount, received_amount, fiscal_year, month,
						 ministry_agency, department
                                                 from `tabRental Bill`
						 where 	docstatus = 1
		                                 and received_amount < receivable_amount
			                         {0}
						 order by tenant_name	
					""".format(condition), as_dict=True)
		else:
			if self.tenant:
				condition += " and tenant = '{0}'".format(self.tenant)

			bill_lists = frappe.db.sql("""
			                         select name, tenant, tenant_name, customer_code, cid, rent_amount, receivable_amount, received_amount, fiscal_year, month,
						 ministry_agency, department
                                                 from `tabRental Bill`
						 where 	docstatus = 1
		                                 and received_amount < receivable_amount
			                         {0}
						 order by tenant_name
					""".format(condition), as_dict=True)
		for a in bill_lists:
			if a.received_amount == 0.00:
				data.append({"bill_no":a.name, "tenant":a.tenant, "tenant_name":a.tenant_name, "customer_code":a.customer_code, "cid":a.cid, "rent_amount":a.rent_amount, "receivable_amount":a.receivable_amount, "fiscal_year":a.fiscal_year, "month":a.month, "ministry_agency": a.ministry_agency, "department":a.department})
			else:
				balance = flt(a.receivable_amount) - flt(a.received_amount)
				if balance > 0:
					data.append({"bill_no":a.name, "tenant":a.tenant, "tenant_name":a.tenant_name, "customer_code":a.customer_code, "cid":a.cid, "rent_amount":a.rent_amount, "receivable_amount":balance, "fiscal_year":a.fiscal_year, "month":a.month, "ministry_agency": a.ministry_agency, "department":a.department})

		return data	

@frappe.whitelist()
def get_tds_account():
	return frappe.db.get_single_value("Accounts Settings", "tds_deducted")			
