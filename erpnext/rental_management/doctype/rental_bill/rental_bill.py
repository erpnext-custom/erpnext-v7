# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, nowtime, getdate, nowdate

class RentalBill(Document):
	def autoname(self):
		if not self.customer_code:
			customer_code = frappe.db.get_value("Customer", {"customer_id":self.cid}, "customer_code")
			if not customer_code:
				frappe.throw("No Customer Code for Tenant CID : {}. Tenant CID might have changed".format(self.tenant))
		else:
			customer_code = self.customer_code
		
		bill_code = "NHDCL/" + str(customer_code) + "/" + str(self.fiscal_year) + str(self.month) + '/.#####'
		self.name = make_autoname(bill_code)

	def on_cancel(self):
		if frappe.db.exists("Rental Advance Adjustment", {"tenant":self.tenant}):
			if frappe.db.exists("Rental Advance Adjusted", {"rental_bill":self.name}):
				rental_adjustment_no = frappe.db.get_value("Rental Advance Adjusted", {"rental_bill":self.name}, "parent")
				frappe.throw("This rental bill is linked with Rental Advance Adjustment No. {}".format(rental_adjustment_no))

			'''
				frappe.db.sql("Delete from `tabRental Advance Adjusted` where rental_bill = '{}'".format(self.name))
			doc = frappe.get_doc("Rental Advance Adjustment", {"tenant":self.tenant})
			
			total_adjusted = total_advance = 0.00
			if doc.advance_adjusted_item:
				for a in doc.advance_adjusted_item:
					total_adjusted += flt(a.adjusted_amount)

			if doc.advance_received_item:
				for a in doc.advance_received_item:
					total_advance += flt(a.balance_amount)

			doc.advance_received = flt(total_advance)
			doc.advance_adjusted = flt(total_adjusted)
			doc.advance_balance = flt(total_advance) - flt(total_adjusted) 
			doc.save()
			'''
