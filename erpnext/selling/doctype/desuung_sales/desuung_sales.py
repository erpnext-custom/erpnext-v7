# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.accounts.general_ledger import make_gl_entries
from frappe import _
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import check_future_date

class DesuungSales(AccountsController):
	#code to fetch selling price for items after selecting item_code
	def get_selling_price(self, item_code = None, branch = None, posting_date = None):
		selling_price = ""
		if not branch or branch == None:
			frappe.throw("Please select branch first")
		else:
			selling_price = frappe.db.sql("""
				SELECT 
					spr.selling_price as selling_price, sp.name as name 
				FROM `tabSelling Price Rate` spr, `tabSelling Price` sp, `tabSelling Price Branch` spb 
				WHERE spr.parent = spb.parent 
				AND spr.particular = {0} 
				AND spb.branch = '{1}' 
				AND '{2}' BETWEEN sp.from_date 
				AND sp.to_date""".format(item_code, branch, posting_date), as_dict = True)
		return selling_price
	#end

	def validate(self):
		check_future_date(self.posting_date)
		self.get_amount()
	
	def get_amount(self):
		Amount = 0
		for item in self.items:
			if not item.qty or not item.rate:
				frappe.throw("Please enter qty or rate")
			item.amount += flt(item.qty) * flt(item.rate)
			Amount += item.amount
		self.total = Amount
	
	def on_submit(self):
		self.post_gl_entry()
		#self.consume_budget()
	
	def on_cancel(self):
		self.post_gl_entry()
		#self.cancel_budget_entry()

	def post_gl_entry(self):
		gl_entries = []
		if self.company == "De-Suung":
			gl_entries.append(
				self.get_gl_dict({
						"account": self.debit_account,
						"debit": self.total,
						"debit_in_account_currency": self.total,
						"voucher_no": self.name,
						"voucher_type": self.doctype,
						"cost_center": self.cost_center,					
						"company": self.company,
						"remarks": self.remarks,
						"business_activity": self.business_activity,
					})
				)
			gl_entries.append(
				self.get_gl_dict({
						"account": self.credit_account,
						"credit": self.total,
						"credit_in_account_currency": self.total,
						"voucher_no": self.name,
						"voucher_type": self.doctype,
						"cost_center": self.cost_center,
						"company": self.company,
						"remarks": self.remarks,
						"business_activity": self.business_activity,
					})
				)
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)


	# @frappe.whitelist()
	# def item_query(filters=None):
    # 	data = frappe.db.sql(
	# 		"""
    #     	SELECT item_group 
    #     	FROM `tabItem`
    #     	WHERE docstatus < 2 
	# 		"""
    # 	)
	# 	return data
# 'party': self.party,
# 'party_type': self.party_type,