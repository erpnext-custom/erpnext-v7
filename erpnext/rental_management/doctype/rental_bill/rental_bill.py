# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, nowtime, getdate, nowdate
from erpnext.accounts.general_ledger import make_gl_entries
from frappe import msgprint

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
		frappe.db.sql("delete from `tabGL Entry` where voucher_no = '{}'".format(self.name))