# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt,cint
from erpnext.custom_utils import prepare_gl, check_future_date

class HSDPayment(Document):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_allocated_amount()
		self.clearance_date = None
				
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

	def on_update_after_submit(self):
		frappe.db.sql('''update `tabGL Entry` set reference_no="{}", reference_date="{}" 
			where voucher_no="{}" '''.format(self.cheque__no, self.cheque_date, self.name))

	def on_cancel(self):
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		
		self.adjust_outstanding(cancel=True)
		self.update_general_ledger()
	
	def adjust_outstanding(self, cancel=False):
		for a in self.items:
			doc = frappe.get_doc("POL", a.pol)
			if doc:
				if doc.docstatus != 1:
					frappe.throw("<b>"+ str(doc.name) +"</b> is not a submitted Issue POL Transaction")
				if cancel:
					doc.db_set("paid_amount", flt(doc.paid_amount) - flt(a.allocated_amount))
					doc.db_set("outstanding_amount", flt(doc.outstanding_amount) + flt(a.allocated_amount))	
				else:
					paid_amount = flt(flt(doc.paid_amount) + flt(a.allocated_amount))
					if round(paid_amount,2) > round(flt(doc.total_amount),2):
						frappe.throw("Paid Amount cannot be greater than the Total Amount for Receive POl <b>"+str(a.pol)+"</b>")
					doc.db_set("paid_amount", paid_amount)
					doc.db_set("outstanding_amount", a.balance_amount)	

	def update_general_ledger(self):
		gl_entries = []
		
		creditor_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		if not creditor_account:
			frappe.throw("Set Default Payable Account in Company")


		if cint(self.final_settlement) ==1:
			gl_entries.append(
				prepare_gl(self, {"account": self.bank_account,
					"credit": flt(self.amount),
					"credit_in_account_currency": flt(self.amount),
					"cost_center": self.cost_center,
					"party_type": "Supplier",
					"party": self.supplier,
					"reference_no": self.cheque__no,
					"reference_date": self.cheque_date
					})
				)
		else:
			 gl_entries.append(
				prepare_gl(self, {"account": self.bank_account,
						"credit": flt(self.amount),
						"credit_in_account_currency": flt(self.amount),
						"cost_center": self.cost_center,
						"reference_no": self.cheque__no,
						"reference_date": self.cheque_date
					})
				)

		gl_entries.append(
			prepare_gl(self, {"account": creditor_account,
					"debit": flt(self.amount),
					"debit_in_account_currency": flt(self.amount),
					"cost_center": self.cost_center,
					"party_type": "Supplier",
					"party": self.supplier,
					"reference_no": self.cheque__no,
					"reference_date": self.cheque_date
				})
			)

		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)

	def get_invoices(self):
		if not self.fuelbook:
			frappe.throw("Select a Fuelbook to Proceed")
		query = """select name as pol, pol_type as pol_item_code, 
						outstanding_amount as payable_amount, 
						item_name, memo_number 
					from tabPOL where docstatus = 1 
					and outstanding_amount > 0 
					and fuelbook = '{0}'
					and posting_date between '{1}' and '{2}'
					order by posting_date, posting_time""".format(self.fuelbook,self.from_date,self.to_date)
		entries = frappe.db.sql(query, as_dict=True)
		self.set('items', [])

		total_amount = 0
		for d in entries:
			total_amount+=flt(d.payable_amount)
			d.allocated_amount = d.payable_amount
			d.balance_amount = 0
			row = self.append('items', {})
			row.update(d)
		self.amount = total_amount
		self.actual_amount = total_amount

