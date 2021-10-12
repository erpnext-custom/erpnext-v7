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
		self.update_rental_official()
		self.generate_penalty()
		self.calculate_discount()
		self.calculate_totals()
	
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
			if a.amount_received > a.amount:
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

	def calculate_discount(self):
		if self.discount_percent > 0:
			discount_amount = 0.00
			for a in self.item:
				if not a.dont_apply_discount:
					discount = round(flt(a.bill_amount) * flt(self.discount_percent)/100)
					a.discount_amount = flt(discount)
					discount_amount += flt(discount)
			self.discount_amount = discount_amount

	def calculate_totals(self):	
		if not self.individual_payment:
			self.tenant = ""
			self.tenant_name = ""
		rent_received = total_amount_received = security_deposit = excess = pre_rent = tds_amount = 0.00
		for a in self.item:
			rent_received_amt = flt(a.rent_received) + flt(a.tds_amount) + flt(a.discount_amount)
			a.total_amount_received = flt(a.rent_received) + flt(a.sa_amount) + flt(a.penalty) + flt(a.excess_amount) + flt(a.pre_rent_amount)
			a.balance_rent = flt(a.bill_amount) - flt(a.rent_received) - flt(a.tds_amount) - flt(a.discount_amount)

			if flt(rent_received_amt) > flt(a.bill_amount):
				a.rent_received = flt(a.bill_amount) - flt(a.tds_amount) - flt(a.discount_amount)
				a.balance_rent = flt(a.bill_amount) - flt(a.rent_received) - flt(a.tds_amount) - flt(a.discount_amount)
				
				frappe.msgprint("Rent Received amount is changed to {} as the total of Rent receive + Discount + TDS cannot be more than Bill Amount {} for tenant {}".format(a.rent_received, a.bill_amount, a.tenant_name))
			
			if a.balance_rent > 0 and (a.pre_rent_amount > 0 or a.excess_amount > 0):
				frappe.throw("Pre rent and excess rent collection not allowed as current rent is not settled")

			tds_amount += flt(a.tds_amount)
			rent_received += flt(a.rent_received)
			security_deposit += flt(a.sa_amount)
			excess += flt(a.excess_amount)
			pre_rent += flt(a.pre_rent_amount)
			total_amount_received += flt(a.rent_received) + flt(a.sa_amount) + flt(a.penalty) + flt(a.excess_amount) + flt(a.pre_rent_amount)

		self.rent_received = rent_received
		self.security_deposit = security_deposit
		self.excess_amount = excess
		self.pre_rent_amount = pre_rent
		self.tds_amount = tds_amount
		self.total_amount_received = flt(total_amount_received)
		if self.tds_amount > 0 and not self.tds_account:
			frappe.throw("Please select TDS Account")

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
				if not a.write_off_penalty and a.bill_amount:
					if a.auto_calculate_penalty:
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
								penalty_on = 0.00
								if not a.dont_apply_discount and a.discount_amount > 0:
									penalty_on = flt(a.bill_amount) - flt(a.discount_amount)
								else:
									penalty_on = flt(a.bill_amount)
								penalty_amt =  flt(penalty_rate)/100.00 * flt(months +1) * flt(penalty_on)
							a.penalty = round(penalty_amt)
							total_penalty += a.penalty
						else:
							frappe.throw("Penalty Rate and Payment Due Date are missing in Rental Setting")
					else:
						if a.penalty > 0:
							total_penalty += a.penalty
				else:
					a.penalty = 0.00					
			self.penalty_amount = round(total_penalty)
		else:
			for a in self.item:
				a.write_off_penalty = 1
				a.penalty = 0.00
			self.penalty_amount = 0.00

	def update_rental_bill(self):					
		if self.docstatus == 1:
			for a in self.get('item'):
				if a.rental_bill:
					doc = frappe.get_doc("Rental Bill", a.rental_bill)
					doc.append("rental_bill_received",{
									"reference_type"   : "Rental Payment",
									"reference"        : self.name,
									"received_amount"  : flt(a.rent_received),
									"pre_rent_amount"  : flt(a.pre_rent_amount),
									"discount_amount"  : flt(a.discount_amount),
									"tds_amount" 	   : flt(a.tds_amount)
								})
					doc.received_amount = flt(doc.received_amount) + flt(a.rent_received)
					doc.pre_rent_amount = flt(doc.pre_rent_amount) + flt(a.pre_rent_amount)
					doc.tds_amount = flt(doc.tds_amount) + flt(a.tds_amount)
					doc.discount_amount = flt(doc.discount_amount) + flt(a.discount_amount)
					doc.penalty = flt(doc.penalty) + flt(a.penalty)
					doc.save()
		else:
			for a in self.get('item'):
				if a.rental_bill:
					doc = frappe.get_doc("Rental Bill", a.rental_bill)
					doc.received_amount = flt(doc.received_amount) - flt(a.rent_received)
					doc.pre_rent_amount = flt(doc.pre_rent_amount) - flt(a.pre_rent_amount)
					doc.tds_amount = flt(doc.tds_amount) - flt(a.tds_amount)
					doc.discount_amount = flt(doc.discount_amount) - flt(a.discount_amount)
					doc.penalty = flt(doc.penalty) + flt(a.penalty)
					doc.save()
			frappe.db.sql("delete from `tabRental Bill Received` where reference='{0}'".format(self.name))
			frappe.db.commit()

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
		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		business_activity = frappe.db.get_single_value("Rental Setting", "business_activity")
		debtor_rental = frappe.db.get_single_value("Rental Account Setting", "revenue_claim_account")
		pre_rent_account = frappe.db.get_single_value("Rental Account Setting", "pre_rent_account")
		penalty_account = frappe.db.get_single_value("Rental Account Setting", "penalty_account")
		excess_payment_account = frappe.db.get_single_value("Rental Account Setting", "excess_payment_account")
		discount_account = frappe.db.get_single_value("Rental Account Setting", "discount_account")
		security_deposit_account = frappe.db.get_single_value("Rental Account Setting", "security_deposit_account")
		
		gl_entries.append(
			self.get_gl_dict({
				"account": self.bank_account,
				"debit": self.total_amount_received,
				"debit_in_account_currency": self.total_amount_received,
				"voucher_no": self.name,
				"voucher_type": "Rental Payment",
				"cost_center": cost_center,
				"company": self.company,
				"remarks": self.remarks,
				"business_activity": business_activity
			})
		)
		
		for a in self.get('item'):
			# frappe.throw(a.tenant)
			party_name = frappe.db.get_value("Customer", {"customer_code": frappe.db.get_value("Tenant Information", a.tenant, "customer_code")},"name")
			account_type = frappe.db.get_value("Account", debtor_rental, "account_type") or ""
			# frappe.throw(party_name)
			if account_type in ["Receivable", "Payable"]:
				party = party_name
				party_type = "Customer"
			else:
				party = None
				party_type = None

			debtor_amount = flt(a.rent_received) + flt(a.discount_amount) + flt(a.tds_amount)
			if debtor_amount > 0:
				gl_entries.append(
					self.get_gl_dict({
						"account": debtor_rental,
						"credit": debtor_amount,
						"credit_in_account_currency": debtor_amount,
						"voucher_no": self.name,
						"voucher_type": "Rental Payment",
						"cost_center": cost_center,
						"party": party,
						"party_type": party_type,
						"company": self.company,
						"remarks": self.remarks,
						"business_activity": business_activity
					})
				)
			if a.pre_rent_amount > 0:
				account_type = frappe.db.get_value("Account", pre_rent_account, "account_type") or ""
				if account_type in ["Receivable", "Payable"]:
					party = party_name
					party_type = "Customer"
				else:
					party = None
					party_type = None

				gl_entries.append(
					self.get_gl_dict({
						"account": pre_rent_account,
						"credit": flt(a.pre_rent_amount),
						"credit_in_account_currency": flt(a.pre_rent_amount),
						"voucher_no": self.name,
						"voucher_type": "Rental Payment",
						"cost_center": cost_center,
						"party": party,
						"party_type": party_type,
						"company": self.company,
						"remarks": self.remarks,
						"business_activity": business_activity
					})
				)
			
			if a.sa_amount > 0:
				account_type = frappe.db.get_value("Account", security_deposit_account, "account_type") or ""
				if account_type in ["Receivable", "Payable"]:
					party = party_name
					party_type = "Customer"
				else:
					party = None
					party_type = None
				gl_entries.append(
					self.get_gl_dict({
						"account": security_deposit_account,
						"credit": flt(a.sa_amount),
						"credit_in_account_currency": flt(a.sa_amount),
						"voucher_no": self.name,
						"voucher_type": "Rental Payment",
						"cost_center": cost_center,
						"party": party,
						"party_type": party_type,
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
		
		if self.discount_amount > 0:
			gl_entries.append(
				self.get_gl_dict({
					"account": discount_account,
					"debit": self.discount_amount,
					"debit_in_account_currency": self.discount_amount,
					"voucher_no": self.name,
					"voucher_type": self.doctype,
					"cost_center": cost_center,
					"company": self.company,
					"remarks": self.remarks,
					"business_activity": business_activity
					})
				)
		if self.penalty_amount > 0 and not self.write_off_penalty:
			gl_entries.append(
				self.get_gl_dict({
					"account": penalty_account,
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

		if self.excess_amount > 0:
			gl_entries.append(
				self.get_gl_dict({
					"account": excess_payment_account,
					"credit": self.excess_amount,
					"credit_in_account_currency": self.excess_amount,
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
		else:
			if self.tenant:
				condition += " and tenant = '{0}'".format(self.tenant)
		self.set('item', [])
		bill_amount = 0.00
		for i in frappe.db.sql("""select name as rental_bill, tenant, tenant_name, customer_code, cid, 
						(receivable_amount - received_amount - discount_amount - tds_amount - adjusted_amount) as bill_amount, fiscal_year, month,
						ministry_agency, department
						from `tabRental Bill`
						where docstatus = 1 and (receivable_amount - received_amount - discount_amount - tds_amount - adjusted_amount) > 0
						{0} order by tenant_name
				""".format(condition), as_dict=True):
			row = self.append('item', {})
			row.rent_received = flt(i.bill_amount)
			row.total_amount_received = flt(i.bill_amount)
			row.auto_calculate_penalty = 1
			bill_amount += flt(i.bill_amount)
			row.update(i)
		return bill_amount

@frappe.whitelist()
def get_tds_account():
	return frappe.db.get_single_value("Accounts Settings", "tds_deducted")			
