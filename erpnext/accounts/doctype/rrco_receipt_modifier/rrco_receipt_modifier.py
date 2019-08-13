# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RRCOReceiptModifier(Document):
	def validate(self):
		self.check_duplicate_entries()
		if not self.from_date or not self.to_date:
			frappe.throw("From Date and To Date is Mandiatory")

		if self.to_date < self.from_date:
                        frappe.throw(" To Date Cannot be Earlier then From Date")

		if not self.get("items"):
			frappe.throw("Item List Is Mandiatory")

		#self.update_rrco_entries()

	#patch to update RRCO Receipt Entries
	def update_rrco_entries(self):
		import re
		pi = '^PI'
		dp = '^DP'
		le = '^EMP'
		for a in frappe.db.sql("select name, purchase_invoice from `tabRRCO Receipt Entries`", as_dict =1):
			if re.match(pi, str(a.purchase_invoice)):
				doc = frappe.get_doc("Purchase Invoice", a.purchase_invoice)

			if re.match(dp, str(a.purchase_invoice)):
				doc = frappe.get_doc("Direct Payment", a.purchase_invoice)
			
			frappe.db.sql(""" update `tabRRCO Receipt Entries` set purpose = 'Purchase Invoices', supplier = '{0}'  where name ='{1                                                  }'""".format(self.supplier, a.name))

			if re.match(le, str(a.purchase_invoice)):
				frappe.db.sql(""" update `tabRRCO Receipt Entries` set purpose = 'Leave Encashment', supplier = ''
				where name = '{0}'
				""".format(a.name))

	#Cancel the Receipt
	def on_submit(self):
		for a in self.get("items"):
                        #frappe.db.sql("update `tabRRCO Receipt Entries` set docstatus = 2 where name = '{0}'".format(a.receipt_no))	
			frappe.db.sql(" delete  from `tabRRCO Receipt Entries` where name = '{0}'".format(a.receipt_no))

	#Populate RRCO Receipt Entries
	def get_entries(self):
		purpose = " 1 = 1"
		supplier = " 1 = 1"
		if self.purpose:
			purpose = " purpose = '{0}'".format(self.purpose)
		
		if self.purpose == "Purchase Invoices":
			supplier = " supplier = '{0}'".format(self.supplier)

		date = " between '{0}' and '{1}'".format(self.from_date, self.to_date)
		query = """ select name as receipt_no, receipt_date, receipt_number, purchase_invoice, cheque_number, 
			cheque_date from `tabRRCO Receipt Entries` 
			where docstatus =1 and receipt_date {0} and {1} and {2}""".format(date, purpose, supplier)
		entries = frappe.db.sql(query, as_dict=True)
		self.set('items', [])
		for d in entries:
			row = self.append('items', {})
			row.update(d)

	#check duplicate entries
	def check_duplicate_entries(self):
		found = []
		for a in self.get("items"):
			if a.receipt_no in found:
				frappe.throw(" <b> {0} </b> already added in the List".format(a.receipt_no))
			else:
				found.append(a.receipt_no)
