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
		self.calculate_total()

	def validate_items(self):
		for a in self.items:
			if not flt(a.qty) > 0:
				frappe.throw("Volume cannot be zero or less")
			if not flt(a.diameter) > 0:
				frappe.throw("Diameter cannot be zero or less")

	def calculate_total(self):
		records = frappe.db.sql("select b.class as timber_class, sum(a.qty)*35.315 as total_quantity from `tabMarking List Item` a, `tabTimber Class` b where a.species = b.name and a.parent = %s group by b.class", self.name, as_dict=1)
		self.set('aggregate_items', [])

		total_amount = 0
                for d in records:
                        row = self.append('aggregate_items', {})
                        row.update(d)
			total_amount += d.total_quantity

		self.total_amount = total_amount
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
		#if not bank_account:
		#	frappe.throw("Setup Expense Bank Account in Branch")	

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
		#je.save()
		#self.db_set("journal_entry", je.name)
		self.journal_entry = "ISNIDE"
		frappe.reload_doctype(self.doctype)
		#frappe.reload_doc(frappe.db.get_value("Doctype", self.doctype, "module"), self.doctype, self.name, 1)
		frappe.msgprint("RELOAD")		

