# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from erpnext.accounts.utils import get_fiscal_year, now
from frappe.utils import flt, getdate, formatdate
from frappe.model.document import Document

class OvertimeApplication(Document):
	def validate(self):
		self.validate_dates()
		#self.calculate_totals()
		self.calculate_amount()
		self.processed = 0

	def on_submit(self):
		enable_ot_bulk_payment = frappe.db.get_single_value("HR Settings", "enable_bulk_ot_payment")
		if not enable_ot_bulk_payment:
			self.check_status()
			#self.validate_submitter()
			#Commented by Tashi on 18-02-2022 as ot is processed with salary
			#self.post_journal_entry()

	def on_cancel(self):
		self.check_workflow_state()
		self.db_set("status", "Rejected")
		#enable_ot_bulk_payment = frappe.db.get_single_value("HR Settings", "enable_bulk_ot_payment")
		#if not enable_ot_bulk_payment:		
		self.check_journal()
		#self.update_salary_structure(cancel = True)	
	'''def calculate_totals(self):
                total_hours  = 0
                for i in self.items:
                        total_hours += flt(i.number_of_hours)

                self.total_hours  = flt(total_hours)
                self.total_amount = flt(total_hours)*flt(self.rate)

                if flt(self.total_hours) <= 0:
                        frappe.throw(_("Total number of hours cannot be nil."),title="Incomlete information")'''

	def check_status(self):
		if self.status != "Approved":
			frappe.throw("Only Approved documents can be submitted")

	def check_workflow_state(self):
		if self.workflow_state == 'Approved' and self.docstatus != 1:
			self.workflow_state = 'Waiting Approval'
	##
	# Dont allow duplicate dates
	##
	def validate_dates(self):
		for a in self.items:
                        if not a.date:
                                frappe.throw(_("Row#{0} : Data cannot be blank").format(a.idx),title="Invalid Date")
                                
			for b in self.items:
				if a.date == b.date and a.idx != b.idx:
					frappe.throw("Duplicate Dates in row " + str(a.idx) + " and " + str(b.idx))

	##
	# Allow only the approver to submit the document
	##
	def validate_submitter(self):
		if self.workflow_state == "Waiting Approval":
			if self.approver != frappe.session.user:
				frappe.throw("Only the selected Approver can submit this document")


	def get_basic_salary(self):
			if self.employee:
				# Get basic pay from the active salary structure
				sst_doc = frappe.get_doc("Salary Structure",frappe.db.get_value('Salary Structure', {'employee': self.employee, 'is_active' : 'Yes'}, "name"))
				for d in sst_doc.earnings:
					if d.salary_component == 'Basic Pay':
						basic        = flt(d.amount)
						#number of month is uniformly taken as 30 as per SMCL Rule
						rate_per_day = flt(basic)/30
						rate_per_hour = flt(rate_per_day)/8
						self.rate = rate_per_hour

	def calculate_amount(self):
		holiday_list = get_holiday_list_for_employee(self.employee)
                amount = 0.0
                hour = 0.0
		night_shift_bonus = 0.0
                for d in self.items:
			ot_base = 1
			holiday_bonus = 0
			d.is_holiday = 0
			if frappe.db.exists("Holiday", {"parent": holiday_list, "holiday_date": str(d.date)}):
				d.is_holiday = 1
				holiday_bonus = 0.5
				
			if d.is_night_shift:
				night_shift_bonus = 0.5
			amount += (self.rate*(ot_base+holiday_bonus+night_shift_bonus))*flt(d.number_of_hours)
			hour += flt(d.number_of_hours)

		self.total_hours = hour
		self.total_amount = amount
		if flt(self.total_amount) <= 0:
                        frappe.throw(_("Total amount cannot be nil."),title="Incomlete information")

	

	#Update Salary Structure
	def update_salary_structure(self, cancel=False):
		if frappe.db.exists("Salary Structure", {"employee": self.employee, "is_active": "Yes"}):
                	doc = frappe.get_doc("Salary Structure", {"employee": self.employee, "is_active": "Yes"})
			frappe.db.sql(""" delete from `tabOvertime Item` where parent = '{0}' and (processed = 1 or reference = '{1}')			""".format(doc.name, self.name))
			if cancel:
				frappe.db.sql(""" delete 
						from `tabOvertime Item` 
						where reference = '{0}' and parent = '{1}'
				""".format(self.name, doc.name))
			else:
				row = doc.append("ot_items",{})
                                row.reference    = self.name
                                row.ot_date      = self.posting_date
                                row.hourly_rate  = self.rate
                                row.total_hours  = self.total_hours
                                row.total_amount = self.total_amount
			doc.save(ignore_permissions=True)

		else:
			frappe.throw(_("No active salary structure found for employee {0} {1}").format(self.employee, self.employee_name), title="No Data Found")


	##
	# Post journal entry
	##
	def post_journal_entry(self):	
		cost_center = frappe.db.get_value("Employee", self.employee, ["cost_center"])
		ot_account = frappe.db.get_single_value("HR Accounts Settings", "overtime_account")
		#following code commented as per ticket #282 and subsequent added
		expense_bank_account = frappe.db.get_value("HR Accounts Settings", None, "employee_payable_account")
		#expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
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
				"party_type": "Employee",
				"party": self.employee,
				"cost_center": cost_center,
				"credit_in_account_currency": flt(total_amount),
				"credit": flt(total_amount),
			})
		
		je.append("accounts", {
				"account": ot_account,
				"cost_center": cost_center,
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
		
		self.db_set("payment_jv", None)
