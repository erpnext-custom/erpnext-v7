# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, cint, cstr, flt, fmt_money, formatdate, nowdate
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import generate_receipt_no, check_future_date, get_branch_cc
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba

class MechanicalPayment(AccountsController):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_allocated_amount()
		self.validate_delivery_note()
		self.validate_technical_sanction()
		self.set_missing_values()
		self.clearance_date = None

	def set_missing_values(self):
		self.cost_center = get_branch_cc(self.branch)
		if self.payment_for == "Transporter Payment":
			self.transportation_account = frappe.db.get_value('Production Account Settings',{'company': self.company},'transportation_account') 
			if self.tds_amount:
				self.net_amount = self.total_amount - (self.tds_amount + self.other_deduction)
			else:
				self.net_amount = self.total_amount - self.other_deduction
		if self.payment_for == "Job Card" and self.tds_amount:
				self.net_amount = self.payable_amount - self.tds_amount
	
		if not self.net_amount:
			frappe.throw("Net Amount cannot be less than Zero")
		if flt(self.tds_amount) < 0:
			frappe.throw("TDS Amount cannot be less than Zero")

	def validate_allocated_amount(self):
		if not self.receivable_amount > 0 and self.payment_for not in ["Transporter Payment","Maintenance Payment"] and not self.payable_amount:
			frappe.throw("Amount should be greater than 0")	
		to_remove = []
		if self.payment_for != "Job Card": 
			total = flt(self.receivable_amount)
		if self.payment_for == "Job Card": 
			total = flt(self.payable_amount)
		total_actual = 0
		for d in self.items:
			allocated = 0
			if total > 0 and total >= d.outstanding_amount:
				allocated = d.outstanding_amount
				total_actual += flt(d.outstanding_amount)
			elif total > 0 and total < d.outstanding_amount:
				total_actual += flt(d.outstanding_amount)
				allocated = total
			else:
				allocated = 0
		
			d.allocated_amount = allocated
			total-=allocated
			if d.allocated_amount == 0:
				to_remove.append(d)

		[self.remove(d) for d in to_remove]
		self.actual_amount = total_actual 
		
		if self.receivable_amount > self.actual_amount:
			frappe.throw("Receivable Amount Cannot be grater than Total Outstanding Amount")
	def validate_delivery_note(self):
		if self.payment_for == "Transporter Payment":
			for d in self.transporter_payment_item:
				dtl = frappe.db.sql("select t.delivery_note as dn, m.name as mno from `tabMechanical Payment` m,\
						 `tabTransporter Payment Item` t where m.name=t.parent and m.docstatus != 2 and \
						t.delivery_note='{0}'".format(d.delivery_note), as_dict=True)		
				if len(dtl) > 0:
					for a in dtl:
                                		frappe.throw("The Delivery Note {0} is already in use with Payment No. {1}.".format(a.dn,a.mno));

	def validate_technical_sanction(self):
		if self.payment_for == "Maintenance Payment":
			for a in self.maintenance_payment_item:
				dtl = frappe.db.sql("select t.technical_sanction as ts, m.name as mno from `tabMechanical Payment` m,\
                                                 `tabMaintenance Payment Item` t where m.name=t.parent and m.docstatus != 2 and \
                                                t.technical_sanction='{0}' and m.name !='{1}'".format(a.technical_sanction, self.name), as_dict=True)
                                if len(dtl) > 0:
                                        for b in dtl:
                                                frappe.throw("The Technical Sanction {0} is already in used with Payment No. {1}.".format(b.ts,b.mno));

			# Retrieve Default Account for GL
			self.maintenance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "repair_and_maintenance_expense_account")
			if not self.expense_account:
				self.expense_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")

	def on_submit(self):
		self.make_gl_entry()
		self.update_ref_doc()
		self.consume_budget()

	def on_cancel(self):	
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		
		self.make_gl_entry()
		self.update_ref_doc(cancel=1)
		self.cancel_budget_entry()

	def check_amount(self):
		if self.net_amount < 0:
			frappe.throw("Net Amount cannot be less than Zero")
		if self.tds_amount < 0:
			frappe.throw("TDS Amount cannot be less than Zero")
			
	def update_ref_doc(self, cancel=None):
		for a in self.items:
			doc = frappe.get_doc(a.reference_type, a.reference_name)
			if cancel:
				amount = flt(doc.outstanding_amount) + flt(a.allocated_amount)
			else:
				amount = flt(doc.outstanding_amount) -  flt(a.allocated_amount) 

			if a.reference_type == "Job Card":
				payable_amount = doc.total_amount
				self.total_amount = payable_amount
			else:
				payable_amount = doc.balance_amount

			if amount < 0:
				frappe.throw("Outstanding Amount for {0} cannot be less than 0".format(a.reference_name))
			if amount > payable_amount:
				frappe.throw("Outstanding Amount for {0} cannot be greater than payable amount".format(a.reference_name))
				
			doc.db_set("outstanding_amount", amount)
		
		if self.payment_for == "Maintenance Payment":
			for a in self.maintenance_payment_item:
				doc= frappe.get_doc("Technical Sanction Bill", a.technical_sanction)
			if cancel:
				doc.db_set("maintenance_payment","")
			else:
				doc.db_set("maintenance_payment", self.name)

	def get_series(self):
		fiscal_year = getdate(self.posting_date).year
		generate_receipt_no(self.doctype, self.name, self.branch, fiscal_year)

	def make_gl_entry(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		receivable_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_receivable_account")
		#creditor_account  = frappe.db.get_value("Company", "default_payable_account")
		#frappe.msgprint("{0}".format(creditor_account))
		creditor_account= frappe.get_doc("Company", self.company).default_payable_account
		if not receivable_account:
			frappe.throw("Setup Default Receivable Account in Maintenance Setting")
		if not creditor_account:
			frappe.throw("Setup Default Payable Account in Company")

		default_ba = get_default_ba()

		gl_entries = []
		if self.payment_for in ["Transporter Payment","Maintenance Payment"]:
			debit_account = self.transportation_account if self.payment_for == "Transporter Payment" else creditor_account #self.maintenance_account
			party_type = "Supplier" if self.payment_for == "Maintenance Payment" else ""
			party = self.supplier if self.payment_for == "Maintenance Payment" else ""
			gl_entries.append(
				self.get_gl_dict({"account": debit_account,
						 "debit": flt(self.total_amount),
						 "debit_in_account_currency": flt(self.total_amount),
						 "cost_center": self.cost_center,
						 "party_check": 1,
						"party_type": party_type,
						"party": party,
						 "reference_type": self.doctype,
						 "reference_name": self.name,
						 "business_activity": default_ba,
						 "remarks": self.remarks
						})
					)
			if self.other_deduction:
				if not self.other_deduction_account:
					frappe.throw("Required value for Other Deduction Account")
				gl_entries.append(
					self.get_gl_dict({"account": self.other_deduction_account,
							"credit": flt(self.other_deduction),
							"credit_in_account_currency": flt(self.other_deduction),
							"cost_center": self.cost_center,
							"party_check": 1,
						 	"party_type": party_type,
						 	"party": party,
							"reference_type": self.doctype,
							"reference_name": self.name,
							"business_activity": default_ba,
							"remarks": self.remarks
							})
					)
			if self.tds_amount:
				gl_entries.append(
					self.get_gl_dict({"account": self.tds_account,
							 "credit": flt(self.tds_amount),
							 "credit_in_account_currency": flt(self.tds_amount),
							 "cost_center": self.cost_center,
							 "party_check": 1,
							 "reference_type": self.doctype,
							 "reference_name": self.name,
							 "business_activity": default_ba,
							 "remarks": self.remarks
							})
					)
			
			gl_entries.append(
				self.get_gl_dict({"account": self.expense_account,
						 "credit": flt(self.net_amount),
						 "credit_in_account_currency": flt(self.net_amount),
						 "cost_center": self.cost_center,
						 "party_check": 1,
						 "party_type": party_type,
						 "party": party,
						 "reference_type": self.doctype,
						 "reference_name": self.name,
						 "business_activity": default_ba,
						 "remarks": self.remarks
						})
				)
		else:
			if self.receivable_amount:
				gl_entries.append(
				self.get_gl_dict({"account": self.income_account,
						 "debit": flt(self.net_amount),
						 "debit_in_account_currency": flt(self.net_amount),
						 "cost_center": self.cost_center,
						 "party_check": 1,
						 "reference_type": self.doctype,
						 "reference_name": self.name,
						 "business_activity": default_ba,
						 "remarks": self.remarks
						})
				)

				if self.tds_amount:
					gl_entries.append(
						self.get_gl_dict({"account": self.tds_account,
								 "debit": flt(self.tds_amount),
								 "debit_in_account_currency": flt(self.tds_amount),
								 "cost_center": self.cost_center,
								 "party_check": 1,
								 "reference_type": self.doctype,
								 "reference_name": self.name,
								 "business_activity": default_ba,
								 "remarks": self.remarks
								})
						)
				
				gl_entries.append(
					self.get_gl_dict({"account": receivable_account,
							 "credit": flt(self.receivable_amount),
							 "credit_in_account_currency": flt(self.net_amount),
							 "cost_center": self.cost_center,
							 "party_check": 1,
							 "party_type": "Customer",
							 "party": self.customer,
							 "reference_type": self.doctype,
							 "reference_name": self.name,
							 "business_activity": default_ba,
							 "remarks": self.remarks
							})
					)
			else:
				gl_entries.append(
                                self.get_gl_dict({"account": creditor_account,
                                                 "debit": flt(self.payable_amount),
                                                 "debit_in_account_currency": flt(self.payable_amount),
                                                 "cost_center": self.cost_center,
                                                 "reference_type": self.doctype,
						 "party_type": "Supplier",
						 "party": self.supplier,
                                                 "reference_name": self.name,
                                                 "business_activity": default_ba,
                                                 "remarks": self.remarks
                                                })
                                        )
				if self.tds_amount:
					gl_entries.append(
						self.get_gl_dict({"account": self.tds_account,
								 "credit": flt(self.tds_amount),
								 "credit_in_account_currency": flt(self.tds_amount),
								 "cost_center": self.cost_center,
								 "reference_type": self.doctype,
								 "reference_name": self.name,
								 "business_activity": default_ba,
								 "remarks": self.remarks
								})
						)
				gl_entries.append(
					self.get_gl_dict({"account": self.outgoing_account,
							 "credit": flt(self.net_amount),
							 "credit_in_account_currency": flt(self.net_amount),
							 "cost_center": self.cost_center,
							 "reference_type": self.doctype,
							 "reference_name": self.name,
							 "business_activity": default_ba,
							 "remarks": self.remarks
							})
                                	)
	

		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
	##
        # Update the Committedd Budget for checking budget availability
        ##
        def consume_budget(self):
                if self.payment_for == "Transporter Payment":
                        bud_obj = frappe.get_doc({
                                "doctype": "Committed Budget",
                                "account": self.transportation_account,
                                "cost_center": self.cost_center,
                                "po_no": self.name,
                                "po_date": self.posting_date,
                                "amount": self.net_amount,
                                "poi_name": self.name,
                                "date": frappe.utils.nowdate()
                                })
                        bud_obj.flags.ignore_permissions = 1
                        bud_obj.submit()

                        consume = frappe.get_doc({
                                "doctype": "Consumed Budget",
                                "account": self.transportation_account,
                                "cost_center": self.cost_center,
                                "po_no": self.name,
                                "po_date": self.posting_date,
                                "amount": self.net_amount,
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
	

	def get_transactions(self):
		if not self.branch or not self.customer or not self.payment_for:
			frappe.throw("Branch, Customer and Payment For is Mandatory")
		transactions = frappe.db.sql("select name, outstanding_amount from `tab{0}` where customer = '{1}' and branch = '{2}' and outstanding_amount > 0 and docstatus = 1 order by creation".format(self.payment_for, self.customer, self.branch), as_dict=1)
		self.set('items', [])

		total = 0
                for d in transactions:
                        d.reference_type = self.payment_for
			d.reference_name = d.name
			d.allocated_amount = d.outstanding_amount
			row = self.append('items', {})
                        row.update(d)
			total += flt(d.outstanding_amount)
		self.receivable_amount = total
		self.actual_amount = total

@frappe.whitelist()
def get_tds_account(percent):
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
			frappe.throw(
				"Set TDS Accounts in Accounts Settings and try again")
		return frappe.db.get_single_value("Accounts Settings", field)




