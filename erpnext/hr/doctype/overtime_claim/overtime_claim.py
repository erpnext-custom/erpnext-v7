# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint, nowdate, getdate, formatdate
from erpnext.custom_workflow import validate_workflow_states
from erpnext.custom_utils import check_future_date

class OvertimeClaim(Document):
	def validate(self):
		validate_workflow_states(self)
		self.validate_dates()
		self.calculate_totals()
		check_future_date(self.posting_date)
		check_future_date(self.from_date)

	def on_submit(self):
		self.validate_submitter()
		self.post_journal_entry()
		self.update_authorization(action='submit')

	def on_cancel(self):
		self.check_journal()
		self.update_authorization(action='cancel')
	
	def update_authorization(self, action):
		if action == "submit":
			frappe.db.sql("update `tabOvertime Authorization` set `overtime_claim` = '{0}' where name = '{1}'".format(self.name, self.overtime_authorization))
		elif action == "cancel":
			frappe.db.sql("update `tabOvertime Authorization` set `overtime_claim` = NULL where name = '{0}'".format(self.overtime_authorization))
		else:
			pass	

	def calculate_totals(self):
                total_hours  = 0
		if not self.rate or self.rate < 1:
			basic = frappe.db.sql("select a.amount as basic_pay from `tabSalary Detail` a, `tabSalary Structure` b where a.parent = b.name and a.salary_component = 'Basic Pay' and b.is_active = 'Yes' and b.employee = \'" + str(self.employee) + "\'", as_dict=True)
                	if basic:
                        	self.rate = (flt(basic[0].basic_pay) * 1.5) / (30 * 8)
                	else:
                        	frappe.throw("No Salary Structure foudn for the employee")

                for i in self.items:
                        total_hours += flt(i.number_of_hours)

                self.total_hours  = flt(total_hours)
                self.total_amount = flt(total_hours)*flt(self.rate)

                if flt(self.total_hours) <= 0:
                        frappe.throw(_("Total number of hours cannot be nil."),title="Incomlete information")

                
	##
	# Dont allow duplicate dates
	##
	def validate_dates(self):
		for a in self.items:
			check_future_date(a.date)
                        if not a.date:
                                frappe.throw(_("Row#{0} : Data cannot be blank").format(a.idx),title="Invalid Date")
   			elif getdate(self.from_date) > getdate(a.date) or getdate(self.to_date) < getdate(a.date):
				frappe.throw(_("Row#{0} : Date should be within {1} and {2}").format(a.idx, self.from_date, self.to_date), title="Invalid Date Input")
				                             
			for b in self.items:
				if a.date == b.date and a.idx != b.idx:
					frappe.throw("Duplicate Dates in row " + str(a.idx) + " and " + str(b.idx))

	##
	# Allow only the approver to submit the document
	##
	def validate_submitter(self):
		if self.approver != frappe.session.user:
			frappe.throw("Only the selected Approver can submit this document")


	##
	# Post journal entry
	##
	def post_journal_entry(self):	
		cost_center, ba = frappe.db.get_value("Employee", self.employee, ["cost_center", "business_activity"])
		ot_account = frappe.db.get_single_value("HR Accounts Settings", "overtime_account")
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not cost_center:
			frappe.throw("Setup Cost Center for employee in Employee Information")
		if not expense_bank_account:
			frappe.throw("Setup Default Expense Bank Account for your Branch")
		if not ot_account:
			frappe.throw("Setup Default Overtime Account in HR Account Setting")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Payment for Overtime (" + self.employee_name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Payment Paid against : ' + self.name;
		je.posting_date = self.posting_date
		total_amount = self.total_amount
		je.branch = self.branch

		je.append("accounts", {
				"account": expense_bank_account,
				"cost_center": cost_center,
				"business_activity": ba,
				"credit_in_account_currency": flt(total_amount),
				"credit": flt(total_amount),
			})
		
		je.append("accounts", {
				"account": ot_account,
				"cost_center": cost_center,
				"business_activity": ba,
				"debit_in_account_currency": flt(total_amount),
				"debit": flt(total_amount),
				"reference_type": self.doctype,
				"reference_name": self.name
			})

		je.insert()

		self.db_set("payment_jv", je.name)
		frappe.msgprint("Bill processed to accounts through journal voucher " + je.name)


	##
	# Check journal entry status (allow to cancel only if the JV is cancelled too)
	##
	def check_journal(self):
		cl_status = frappe.db.get_value("Journal Entry", self.payment_jv, "docstatus")
		if cl_status and cl_status != 2:
			frappe.throw("You need to cancel the journal entry " + str(self.payment_jv) + " first!")
		
		self.db_set("payment_jv", "")
