# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class ProcessMRPayment(Document):
	def validate(self):
		if self.items:
			total_ot = total_wage = 0
			for a in self.items:
				total_ot += flt(a.total_ot_amount)
				total_wage += flt(a.total_wage)
			total = total_ot + total_wage
			self.wages_amount = total_wage
			self.ot_amount = total_ot
			self.total_overall_amount = total
			

	def on_submit(self):
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not expense_bank_account:
			frappe.throw("Setup Default Expense Bank Account for your Branch")
		ot_account = frappe.db.get_single_value("Projects Accounts Settings", "mr_overtime_account")
		if not ot_account:
			frappe.throw("Setup MR Overtime Account in Projects Accounts Settings")
		wage_account = frappe.db.get_single_value("Projects Accounts Settings", "mr_wages_account")
		if not revenue_bank_account:
			frappe.throw("Setup MR Wages Account in Projects Accounts Settings")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Payment for MR (" + self.project + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Payment against : ' + self.name;
		je.posting_date = self.posting_date
		je.branch = self.branch
		total_amount = self.total_overall_amount

		je.append("accounts", {
				"account": expense_bank_account,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(total_amount),
				"credit": flt(total_amount),
			})
	
		if self.ot_amount:	
			je.append("accounts", {
					"account": ot_account,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.ot_amount),
					"debit": flt(self.ot_amount),
				})

		if self.wages_amount:	
			je.append("accounts", {
					"account": wage_account,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.wages_amount),
					"debit": flt(self.wages_amount),
				})

		je.insert()

@frappe.whitelist()
def get_records(from_date, to_date, project):
	return frappe.db.sql("select a.name, a.person_name, a.id_card, a.rate_per_day, a.rate_per_hour, (select sum(1) from `tabMR Attendance` b where b.muster_roll_employee = a.name and b.date between %s and %s and b.project = %s and b.status = 'Present' and b.docstatus = 1) as number_of_days, (select sum(c.number_of_hours) from `tabOvertime Entry` c where c.number = a.name and c.date between %s and %s and c.project = %s and c.docstatus = 1) as number_of_hours from `tabMuster Roll Employee` a where a.project = %s order by a.person_name", (str(from_date), str(to_date), str(project), str(from_date), str(to_date), str(project), str(project)), as_dict=True)
