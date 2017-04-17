# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TransferCoGM(Document):
	def before_submit(self):
		data = frappe.db.sql("""select name from `tabTransfer CoGM` 
				where cost_center = %s and to_fiscal_year = %s and from_fiscal_year = %s and to_account = %s and from_account = %s and amount = %s and docstatus = 1""", 
				(self.cost_center, self.to_fiscal_year, self.from_fiscal_year, self.to_account, self.from_account, self.amount))
		if data:
			frappe.throw("A Transfer of same parameters has already taken place")

	def on_submit(self):
		self.make_gl_entry()

	def on_cancel(self):
		frappe.db.sql("""delete from `tabGL Entry` where name = %s""", self.gl_entry)
		self.db_set("gl_entry", "")

	def make_gl_entry(self):
		gl = frappe.new_doc("GL Entry");
		gl.flags.ignore_permissions = 1
		gl.posting_date = self.posting_date
		gl.cost_center = self.cost_center
		gl.account = self.to_account
		gl.credit = self.amount
		gl.debit_in_account_currency = self.amount
		gl.fiscal_year = self.to_fiscal_year
		gl.voucher_type = "Transfer CoGM"
		gl.voucher_no = self.name
		gl.submit()

		gl.db_set("is_opening", "Yes")
	
		self.db_set("gl_entry", gl.name)

@frappe.whitelist()
def calculate_amount(fiscal_year=None, account=None):
	if fiscal_year and account:
		amount_data = frappe.db.sql(""" select sum(credit - debit) as amount from `tabGL Entry` 
				where fiscal_year = %s and account = %s 
				and docstatus = 1 and voucher_type != 'Period Closing Voucher'""",
				(fiscal_year, account))
		return amount_data
