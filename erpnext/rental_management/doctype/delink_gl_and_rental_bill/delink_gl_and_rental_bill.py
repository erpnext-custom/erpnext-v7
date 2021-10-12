# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class DelinkGLAndRentalBill(Document):
	def validate(self):
		if not frappe.db.exists("GL Entry", {"voucher_no":self.voucher_no}):
			frappe.msgprint("No such GL Entries with voucher no {}".format(self.voucher_no))

		count = 0
		for a in frappe.db.sql("select count(*) as rental_bill_count from `tabRental Bill` where dzongkhag = '{}' and gl_reference = '{}'".format(self.dzongkhag, self.voucher_no), as_dict=True):
			count = a.rental_bill_count
		
		if count == 0:
			frappe.msgprint("No Rental Bill with GL Reference No. {} and Dzongkhag {}".format(self.voucher_no, self.dzongkhag))

	def on_submit(self):
		if frappe.db.exists("GL Entry", {"voucher_no":self.voucher_no}):	
			frappe.db.sql("delete from `tabGL Entry` where voucher_no='{}'".format(self.voucher_no))
		else:
			frappe.throw("Nothing to remove from GL Entry")

		if frappe.db.exists("Rental Bill", {"gl_reference":self.voucher_no, "dzongkhag": self.dzongkhag}):
			frappe.db.sql("Update `tabRental Bill` set gl_reference = NULL, gl_entry = 0 where gl_reference='{}' and dzongkhag = '{}'".format(self.voucher_no, self.dzongkhag))
		else:
			frappe.throw("No Rental Bills to Update")

