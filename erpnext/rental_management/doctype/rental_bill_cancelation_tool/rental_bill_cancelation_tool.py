# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RentalBillCancelationTool(Document):
	def validate(self):
		if not self.items:
			frappe.throw("No voucher in the item")

	def on_submit(self):
		self.cancel_entries()

	def on_cancel(self):
		frappe.throw("Cancellation of this document is not allowed")

	def cancel_entries(self):
		for i in self.items:
			#cancelling of Rental Bills
			for a in frappe.db.sql("select rental_payment, name from `tabRental Bill` where gl_reference = %s and (rental_payment is not NULL or rental_payment != '')", (str(i.voucher_no)), as_dict=1):
				rental_pay = frappe.db.sql("select name, docstatus from `tabRental Payment` where name = %s and docstatus != 2", (str(a.rental_payment)), as_dict=True)
				if rental_pay:
					frappe.throw("Not able to cancel as Rental Bill {0} is linked with rental Payment no {1}".format(a.name, a.rental_payment))

			#cancelling of GL Entries
			frappe.db.sql("update `tabGL Entry` set docstatus = 2 where voucher_no = %s",(str(i.voucher_no)))
			frappe.db.sql("Update `tabRental Bill` set docstatus = 2 where gl_reference = %s",(str(i.voucher_no)))


	def get_rental_vouchers(self):
		data = []
		'''
		voucher_like = "RB" + str(self.fiscal_year)[2:4] + str(self.month) + "%"	
		vouchers = frappe.db.sql("""
				select distinct(voucher_no) as d_voucher_no from `tabGL Entry` 
				where voucher_type = 'Rental Bill' 
				and fiscal_year = %s 
				and voucher_no like %s 
				and docstatus = 1
				""", (str(self.fiscal_year), str(voucher_like)), as_dict = True)
		'''
		
		vouchers = frappe.db.sql("""
				select distinct(gl_reference) as d_voucher_no
				from `tabRental Bill`
				where fiscal_year = %s
				and month = %s
				and docstatus = 1
				and dzongkhag = %s
				""", (str(self.fiscal_year), str(self.month), str(self.dzongkhag)), as_dict = True)

		for v in vouchers:
			for d in frappe.db.sql("select posting_date, sum(credit) as t_credit, sum(debit) as t_debit from `tabGL Entry` where voucher_no = %s", (str(v.d_voucher_no)), as_dict=1):
				if d.t_credit == d.t_debit:
					data.append({"voucher_no": v.d_voucher_no, "posting_date": d.posting_date, "credit": d.t_credit, "debit":d.t_debit})

		return data
