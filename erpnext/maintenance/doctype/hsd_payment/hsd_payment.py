# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt,cint
from erpnext.custom_utils import prepare_gl, check_future_date
from erpnext.accounts.doctype.business_activity.business_activity import get_default_ba

class HSDPayment(Document):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_pols()
		self.validate_allocated_amount()
		self.clearance_date = None

	def validate_pols(self):
		to_remove = []
		for d in self.items:
			hsd = frappe.db.sql("""
				select sum(b.allocated_amount) as paid_amount from `tabHSD Payment Item` b, `tabHSD Payment` a where b.parent=a.name
				and a.docstatus = 1 and b.pol = '{}' and a.name != '{}'
			""".format(d.pol, self.name), as_dict=1)
			pol = frappe.get_doc("POL",d.pol)
			total_amount = pol.total_amount
			if hsd:
				if flt(hsd[0].paid_amount) == flt(total_amount):
					to_remove.append(d)
					pol.db_set("outstanding_amount",0)
				elif flt(total_amount)-flt(hsd[0].paid_amount) > 0:
					d.allocated_amount = flt(total_amount)-flt(hsd[0].paid_amount)
					pol.db_set("paid_amount",flt(hsd[0].paid_amount))
					pol.db_set("outstanding_amount",flt(total_amount)-flt(hsd[0].paid_amount))
		[self.remove(d) for d in to_remove]

	def validate_allocated_amount(self):
		if not self.amount > 0:
			frappe.throw("Amount should be greater than 0")	
		total = flt(self.amount)
		to_remove = []

		for d in self.items:
			allocated = 0
			if total > 0 and total >= d.payable_amount:
				allocated = d.payable_amount
			elif total > 0 and total < d.payable_amount:
				allocated = total
			else:
				allocated = 0
				to_remove.append(d)
		
			d.allocated_amount = allocated
			d.balance_amount = d.payable_amount - allocated
			total-=allocated

		[self.remove(d) for d in to_remove]

	def on_submit(self):
		self.adjust_outstanding()
		self.update_general_ledger()

	def on_cancel(self):
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		
		self.adjust_outstanding(cancel=True)
		self.update_general_ledger()
	
	def adjust_outstanding(self, cancel=False):
		for a in self.items:
			doc = frappe.get_doc("POL", a.pol)
			if doc:
				if cancel:
					doc.db_set("paid_amount", flt(doc.paid_amount) - flt(a.allocated_amount))
					doc.db_set("outstanding_amount", flt(doc.outstanding_amount) + flt(a.allocated_amount))	
				else:
					if doc.docstatus != 1:
						frappe.throw("<b>"+ str(doc.name) +"</b> is not a submitted Issue POL Transaction")

					paid_amount = flt(doc.paid_amount) + flt(a.allocated_amount)
					if round(paid_amount,2) > round(doc.total_amount,2):
						frappe.throw("Paid Amount cannot be greater than the Total Amount for Receive POL <b>"+str(a.pol)+"</b>"+" paid amount is"+str(paid_amount))
					doc.db_set("paid_amount", paid_amount)
					doc.db_set("outstanding_amount", a.balance_amount)	

	def update_general_ledger(self):
		gl_entries = []
		
		creditor_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		if not creditor_account:
			frappe.throw("Set Default Payable Account in Company")

		default_ba =  get_default_ba()

		if cint(self.final_settlement) ==1:
			gl_entries.append(
				prepare_gl(self, {"account": self.bank_account,
					 "credit": flt(self.amount),
					 "credit_in_account_currency": flt(self.amount),
					 "cost_center": self.cost_center,
					"party_type": "Supplier",
                                         "party": self.supplier,
					"business_activity": default_ba
					})
				)
		else:
			 gl_entries.append(
                                prepare_gl(self, {"account": self.bank_account,
                                         "credit": flt(self.amount),
                                         "credit_in_account_currency": flt(self.amount),
                                         "cost_center": self.cost_center,
                                         "business_activity": default_ba
                                        })
                                )

		gl_entries.append(
			prepare_gl(self, {"account": creditor_account,
					 "debit": flt(self.amount),
					 "debit_in_account_currency": flt(self.amount),
					 "cost_center": self.cost_center,
					 "party_type": "Supplier",
					 "party": self.supplier,
					 "business_activity": default_ba
					})
			)

		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)

	def get_invoices(self):
		if not self.fuelbook:
			frappe.throw("Select a Fuelbook to Proceed")
		query = "select name as pol, pol_type as pol_item_code, outstanding_amount as payable_amount, item_name, memo_number from tabPOL where docstatus = 1 and outstanding_amount > 0 and fuelbook = %s and year(posting_date) <= '{0}'order by posting_date, posting_time".format(str(self.posting_date).split("-")[0])
		entries = frappe.db.sql(query, self.fuelbook, as_dict=True)
		self.set('items', [])

		total_amount = 0
		for d in entries:
			d.allocated_amount = d.payable_amount
			d.balance_amount = 0
			row = self.append('items', {})
			row.update(d)
		self.validate_pols()
		for d in entries:
			total_amount+=flt(d.payable_amount)
		self.amount = total_amount
		self.actual_amount = total_amount

