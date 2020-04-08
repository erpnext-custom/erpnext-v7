# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt
from frappe.model.document import Document
from frappe.core.doctype.user.user import send_sms

class OnlinePayment(Document):
	def validate(self):
		#self.update_customer_order()
		self.make_customer_payment()

	def make_customer_payment(self):
		if self.status == "Successful":
			doc = frappe.new_doc('Customer Payment')
			doc.customer_order = self.customer_order
			doc.mode_of_payment= 'Online Payment'
			doc.approval_status= 'Approved'
			doc.paid_amount    = flt(self.amount)
			doc.online_payment = self.name
			doc.bank_code	   = self.bank_code
			doc.bank_account   = self.bank_account
			doc.transaction_id = self.transaction_id
			doc.transaction_time = self.transaction_time
			doc.save(ignore_permissions=True)
			doc.submit()

			if flt(self.amount):
				msg = "NRDCL has received your payment of Nu. {0} against your order {1}. Tran Ref No {2}".\
					format('{:,.2f}'.format(self.amount), self.customer_order, self.name)
				self.sendsms(msg)

	def sendsms(self,msg=None):
		if not msg:
			return

		mobile_no = frappe.db.get_value("User", self.user, "mobile_no")
		if mobile_no:
			send_sms(mobile_no, msg)

	def update_customer_order(self):
		if self.customer_order:
			co = frappe.get_doc('Customer Order', self.customer_order)
			self.user = co.user
			co.db_set('online_payment', self.name)
			co.db_set('transaction_id', self.transaction_id)
			co.db_set('transaction_time', self.transaction_time)
			co.db_set('transaction_status', self.status)
		else:
			self.user = None
