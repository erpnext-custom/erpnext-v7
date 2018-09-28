# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class MarkingList(Document):
	def validate(self):
		self.validate_items()

	def on_update(self):
		self.calculate_total()
		
	def validate_items(self):
		for a in self.items:
			if not flt(a.qty) > 0:
				frappe.throw("Volume cannot be zero or less")
			if not flt(a.diameter) > 0:
				frappe.throw("Diameter cannot be zero or less")

	def calculate_total(self):
		records = frappe.db.sql("select b.class as timber_class, sum(a.qty) as qty_m3, b.timber_type from `tabMarking List Item` a, `tabTimber Species` b where a.species = b.name and a.parent = %s group by b.class, b.timber_type", self.name, as_dict=1)
		self.set('aggregate_items', [])
		frappe.db.sql("delete from `tabMarking List Aggregate` where parent = %s", self.name)

		total_amount = 0
                for d in records:
			d.qty_cft = d.qty_m3 * 35.315
			if d.timber_type == "Conifer":
				d.log_percent = 60
				d.firewood_percent = 40
			else:
				d.log_percent = 40
				d.firewood_percent = 60
			
			#Change this to get from class
			d.log_rate = 12
			d.firewood_rate = 10

			d.log_amount = d.qty_cft * d.log_rate * flt(d.log_percent)/100 
			d.firewood_amount = d.qty_m3 * d.firewood_rate * flt(d.firewood_percent)/100 
			
			d.royalty_amount = d.log_amount + d.firewood_amount
			total_amount += d.royalty_amount
	
                        row = self.append('aggregate_items', {})
                        row.update(d)
			row.save()

		self.db_set("total_amount", total_amount)
		frappe.reload_doctype(self.doctype)

	def on_submit(self):
		pass

	def calculate_royalty(self):
		total = 0
		for a in self.aggregate_items:
			rate = frappe.db.sql("select ")

	def make_royalty_payment(self):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Royalty payment for (" + self.fmu + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Payment against : ' + self.name;
		je.posting_date = frappe.utils.nowdate()
		je.branch = self.branch

		royalty_account = frappe.db.get_value("Production Account Settings", self.company, "default_royalty_account")
		if not royalty_account:
			frappe.throw("Setup Default Royalty Account in Production Account Settings")	

		bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not bank_account:
			frappe.throw("Setup Expense Bank Account in Branch")	

		je.append("accounts", {
				"account": royalty_account,
				"reference_type": "Marking List",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.total_amount),
				"debit": flt(self.total_amount),
				"business_activity": self.business_activity
			})

		je.append("accounts", {
				"account": bank_account,
				"reference_type": "Marking List",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_amount),
				"credit": flt(self.total_amount),
				"business_activity": self.business_activity
			})
		je.save()
		self.db_set("journal_entry", je.name)
		frappe.reload_doctype(self.doctype)

