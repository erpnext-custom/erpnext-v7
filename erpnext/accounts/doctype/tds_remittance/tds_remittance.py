# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TDSRemittance(Document):
	
	def get_details(self):
		query = "select posting_date, party, invoice_no,taxable_amount, tds_amount from `tabDirect Payment` where tds_percent = '{0}' and docstatus = 1 and posting_date between '{1}' and '{2}'".format(self.tds_rate, self.from_date, self.to_date)

		
			
		entries = frappe.db.sql(query, as_dict=True)
		if not entries:
			frappe.msgprint("No Record Found")

		self.set('items', [])

		for d in entries:
			row = self.append('items', {})
			row.update(d)	
