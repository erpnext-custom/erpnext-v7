# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, getdate, comma_and, cint

class TransporterTripLog(Document):
	def validate(self):
		self.get_transporter_rate()

	def get_transporter_rate(self):
		qty = 0
		for b in self.item:
			rate = 0
			expense_account = 0
			for a in frappe.db.sql(""" select r.name, d.rate, r.expense_account
							from `tabTransporter Rate` r, `tabTransporter Distance Rate` d 
							where r.name = d.parent
							and '{0}' between r.from_date and r.to_date
							and d.distance = '{1}'
							and r.from_warehouse = '{2}'
							""".format(self.posting_date, b.distance, self.warehouse), as_dict=True):
				rate = a.rate
				expense_account = a.expense_account
				transporter_rate = a.name
				
			qty = flt(qty) + flt(b.qty)
			if b.transporter_payment_eligible:
				if not b.equipment:
					frappe.throw("Please insert vehicle")
				if rate > 0:
					b.rate = rate
					b.expense_account = expense_account
					b.transporter_rate = transporter_rate
					if b.qty :
						b.amount = flt(b.rate) * flt(b.qty)
					else:
						frappe.throw("Please provide the Quantity")	
				else:
					frappe.throw("Define Transporter Rate for distance {} in Transporter Rate ".format(b.distance))
			else:
				b.rate = 0
				b.amount = 0
				b.expense_account = ''
		self.total_qty = qty
