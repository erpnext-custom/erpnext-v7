# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt,cint,today,nowdate

class SalaryAdvance(Document):
	def validate(self):
		self.total_claim = flt(self.basic_pay) * flt(self.months)
	
	def on_submit(self):
                self.post_journal_entry()


	def get_basic_salary(self):
		if self.employee:
			sst_doc = frappe.get_doc("Salary Structure",frappe.db.get_value('Salary Structure', {'employee': self.employee, 'is_active' : 'Yes'}, "name"))
			for d in sst_doc.earnings:
				if d.salary_component == 'Basic Pay':
					self.basic_pay = flt(d.amount)

		
	def post_journal_entry(self):
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		ic_account = frappe.db.get_single_value("HR Accounts Settings", "employee_advance_salary")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Salary Advance (" + self.name + ")"
		je.voucher_type = 'Journal Entry'
		je.naming_series = 'Journal Entry'
		je.remark = 'Payment against : ' + self.name;
		je.posting_date = self.posting_date
		je.branch = self.branch

		je.append("accounts", {
				"account":expense_bank_account,
				"business_activity": self.business_activity,
				"reference_name": self.name,
				"reference_type": "Salary Advance",
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.total_claim),
				"debit": flt(self.total_claim),
					})
		je.append("accounts", {
				"account": ic_account,
				"business_activity": self.business_activity,
				"reference_type": "Advance Salary",
				"reference_name": self.name,
				"cost_center": self.issuing_cost_center,
				"credit_in_account_currency": flt(self.total_claim),
				"credit": flt(self.total_claim),
					})
			
		je.save()
