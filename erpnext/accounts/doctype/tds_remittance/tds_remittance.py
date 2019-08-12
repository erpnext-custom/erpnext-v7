# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TDSRemittance(Document):
	def validate(self):
		if self.items:
			total_bill= total_tds = 0
			for d in self.items:
				total_bill += flt(d.bill_amount)
				total_tds += flt(d.tds_amount)
				self.total_tds = total_tds 
				self.total_amount= total_bill	

	def on_submit(self):
		self.post_journal_entry()


	def get_details(self):
		query = """select posting_date, party, invoice_no,taxable_amount as amount, tds_amount from `tabDirect Payment` where tds_percent = '{0}'and posting_date between '{1}' and '{2}' and docstatus =1 union all select posting_date, supplier, name,  tds_taxable_amount, tds_amount from `tabPurchase Invoice` where tds_rate = '{0}' and docstatus =1 and posting_date between '{1}' and '{2}'""".format(self.tds_rate, self.from_date, self.to_date)	

		entries = frappe.db.sql(query, as_dict=True)
		if not entries:
			frappe.msgprint("No Record Found")

		self.set('items', [])

		for d in entries:
			row = self.append('items', {})
			row.update(d)	

	def post_journal_entry(self):
		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title =  self.name
		je.voucher_type = 'Journal Entry'
		je.naming_series = 'Voucher'
		je.remark = 'TDS Remittance against : ' + self.name;
		je.posting_date = self.posting_date
		je.branch = self.branch

		je.append("accounts", {
					"account": self.tds_account,
					"party_type": "Customer",
					"party": '',
					"reference_type": "",
					"reference_name": "",
					"cost_center": cost_center,
					"credit_in_account_currency": flt(self.total_tds),
					"credit": flt(self.total_tds),
					"business_activity" : 'common',
				})

		je.append("accounts", {
					"account": self.account,
					"cost_center": cost_center,
					"debit_in_account_currency": flt(self.total_tds),
					"debit": flt(self.total_tds),
					"business_activity": 'common',	
				})
		je.save()
