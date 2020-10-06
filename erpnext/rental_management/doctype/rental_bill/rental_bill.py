# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, nowtime, getdate, nowdate
from frappe import msgprint

class RentalBill(Document):
	def autoname(self):
                customer_code = frappe.db.get_value("Customer", {"customer_id":self.tenant}, "customer_code")
		#customer_code = frappe.db.get_value("Tenant Information", self.tenant, "customer_code")
                bill_code = "NHDCL/" + customer_code + "/" + self.fiscal_year + self.month + '/.#####'
		#bill_code = "NHDCL/300635/2019/01/00001"
		self.name = make_autoname(bill_code)
	
	def on_cancel(self):
		if frappe.db.exists("Rental Advance Adjustment", {"tenant":self.tenant}):
			if frappe.db.exists("Rental Advance Adjusted", {"rental_bill":self.name}):
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
