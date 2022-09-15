# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, nowdate, formatdate, today, get_first_day, date_diff, add_years, flt

class SupplierMonitoring(Document):
	def validate(self):
		tot = 0.0
		if not self.items:
			frappe.throw("No items found for the the given Purchase Order")
		self.check_requirements()
		self.update_ld()
		self.check_duplicate()
		for a in self.get("items"):
			tot += flt(a.liquidated_damage)
		self.total = tot


	def update_ld(self):
		for a in self.get("items"):
			# if getdate(a.received_date):
			# 	a.days_delayed = date_diff(a.received_date, a.schedule_date)
			a.balance_quantity =flt(a.qty) - flt(a.received_quantity)
			a.received_amount = flt(a.rate) * a.received_quantity
			a.undelivered_amount =flt(a.rate) * a.balance_quantity
			if a.liquidated_damage > 0:
				a.liquidated_damage = flt(a.received_amount) * a.days_delayed * .001
			else:
				a.liquidated_damage == 0
			

	def check_duplicate(self):
		if frappe.db.exists("Supplier Monitoring", {'purchase_order': self.purchase_order, 'docstatus': 1}):
            		frappe.throw(('You have already created a Supplier Monitoring transaction for the purchase Order,  <b>{}</b>, This is the document number <b>{}</b>'.format(self.purchase_order, self.name)))
	

	def get_items(self, po):
		data = frappe.db.sql("""
			SELECT 
				item_code, item_name, uom, qty, rate, amount, schedule_date from `tabPurchase Order Item` 
			WHERE	
			parent = '{0}' 
		""".format(po), as_dict=1)
		
		if not data:
			frappe.throw("No items found for the Purchase Order {}".format(po))
        	self.set('items', [])
        	for d in data:
            		row = self.append('items', {})
            		row.update(d)

	def check_requirements(self):		
		for a in self.get("items"):
			max_amount = flt(a.amount)*.1
			# if getdate(a.received_date) < getdate(a.schedule_date):
			# 	frappe.throw("Received Date Cannot be Earlier than Delivery Date at Row {0}".format(a.idx))
			
			if flt(a.received_quantity) > flt(a.qty):
				frappe.throw("Received Quantity cannot be greater than the PO quantity at Row {}".format(a.idx))
			if flt(a.liquidated_damage) > max_amount:
				frappe.throw("Liquidated Damage cannot be more than the 10% of the PO Amount")
			if flt(a.received_quantity) > a.qty:
				frappe.throw("Received Quantity cannot be more than the PO quantity")

@frappe.whitelist()
def calculate_durations(from_date = None, to_date = None):
	duration = date_diff(to_date, from_date)
	if duration > 100:
		frappe.throw("Days Delayed cannot be more than 100 days")
	elif duration < 0:
		return 0
	else:
		return duration