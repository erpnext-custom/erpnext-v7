# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

################# Created by Cheten Tshering on 5/11/2020 ###############################################
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from datetime import datetime
import frappe, erpnext

class CustomerPendingOrders(Document):
	def validate(self):
		self.validations()
		self.calculate_total()
	def validations(self):
		if self.branch == None:
			frappe.throw("Branch is required")
		if self.posting_date == None:
			frappe.throw("Posting date is required")
		if self.customer == None:
			frappe.throw("Customer is required")
		#cc = frappe.get_value("Customer Pending Orders", "CP00009", "customer")
		# cc = frappe.db.sql(
		# 	""" select customer from `tabCustomer Pending Orders` where name= 'CP00003'"""
		# )
		#frappe.msgprint(cc)
	# 	today = datetime.strftime("%d/%m/%Y")
	# 	date = datetime.datetime.strptime(today, "%d/%m/%Y")
	# 	frappe.msgprint(date)
	# 	if self.posting_date < date and self.posting_date > date:
	# 		frappe.throw("Posting date cannot be less or greater than now date.")
	def calculate_total(self):
		total_amount = 0
		for d in self.item:
			d.amount = d.quantity*flt(d.rate)
			#frappe.msgprint("amount is {}".format(d.amount))
			total_amount += d.amount
			#frappe.msgprint("total amount is {}".format(total_amount))
		self.total = total_amount
	#def on_submit(self):





