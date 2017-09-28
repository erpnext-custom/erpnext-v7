# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, nowdate, money_in_words
from erpnext.accounts.utils import get_account_currency, get_fiscal_year
from frappe.utils.data import add_days

class TravelClaim(Document):

	def validate(self):
		hr_role = frappe.db.get_value("UserRole", {"parent": frappe.session.user, "role": "HR User"}, "role")
		if frappe.session.user == self.supervisor and not self.supervisor_approval:
			self.db_set("supervisor_approved_on", '')
			self.supervisor_approved_on = ''
		if self.supervisor_approved_on and not hr_role:
			frappe.throw("Cannot change records after approval by supervisor")
		self.validate_dates()
		self.check_approval()
		self.update_travel_authorization()
		employee = frappe.db.get_value("Employee", self.employee, "user_id")

		if frappe.session.user == self.owner or frappe.session.user == employee:
			self.db_set("claim_status", "")
			self.sendmail(frappe.db.get_value("Employee", {"user_id": self.supervisor}, "name"), "Travel Claim Submitted", str(self.employee_name) + " has requested you to verify and sign a travel claim")
		elif self.claim_status == "Rejected by Supervisor":
			self.sendmail(self.employee, "Travel Claim Rejected by Supervisor" + str(self.name), "Following remarks has been added by the supervisor: \n" + str(self.reason))
		elif self.claim_status == "Rejected by HR":
			self.sendmail(self.employee, "Travel Claim Rejected by HR" + str(self.name), "Following remarks has been added from HR: \n" + str(self.reason))

		if frappe.session.user == self.supervisor and self.supervisor_approval:
			self.db_set("supervisor_approved_on", nowdate())
		
	def on_update(self):
		self.check_double_dates()

	def on_submit(self):
		self.validate_submitter()
		self.check_status()
		self.post_journal_entry()
		self.update_travel_authorization()

		if self.supervisor_approval and self.hr_approval:
			self.db_set("hr_approved_on", nowdate())
		
		self.sendmail(self.employee, "Travel Claim Approved" + str(self.name), "Your travel claim has been approved and sent to Accounts Section. Kindly follow up.")

	def before_cancel(self):
		cl_status = frappe.db.get_value("Journal Entry", self.claim_journal, "docstatus")
		if cl_status != 2:
			frappe.throw("You need to cancel the claim journal entry first!")
		
		ta = frappe.get_doc("Travel Authorization", self.ta)
		ta.db_set("travel_claim", "")

	def on_cancel(self):
		self.sendmail(self.employee, "Travel Claim Cancelled by HR" + str(self.name), "Your travel claim " + str(self.name) + " has been cancelled by the user")

	def check_double_dates(self):
		if self.items:
			start_date = self.items[0].date
			end_date = self.items[len(self.items) - 1].till_date
			if not end_date:
				end_date = self.items[len(self.items) - 1].date

			tas = frappe.db.sql("select a.name from `tabTravel Claim` a, `tabTravel Claim Item` b where a.employee = %s and a.docstatus = 1 and a.name = b.parent and (b.date between %s and %s or %s between b.date and b.till_date or %s between b.date and b.till_date)", (str(self.employee), str(start_date), str(end_date), str(start_date), str(end_date)), as_dict=True)
			if tas:
				frappe.throw("The dates in your current Travel Claim has already been claimed in " + str(tas[0].name))

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		cost_center = frappe.db.get_value("Employee", self.employee, "cost_center")
		if not cost_center:
			frappe.throw("Setup Cost Center for employee in Employee Information")
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not expense_bank_account:
			frappe.throw("Setup Default Expense Bank Account for your Branch")
		
		gl_account = ""	
		if self.travel_type == "Travel":
			if self.place_type == "In-Country":
				gl_account =  "travel_incountry_account"
			else:
				gl_account = "travel_outcountry_account"
		elif self.travel_type == "Training":
			if self.place_type == "In-Country":
				gl_account = "training_incountry_account"
			else:
				gl_account = "training_outcountry_account"
		else:
			if self.place_type == "In-Country":
				gl_account = "meeting_and_seminars_in_account"
			else:
				gl_account = "meeting_and_seminars_out_account"
		
		expense_account = frappe.db.get_single_value("HR Accounts Settings", gl_account)
		if not expense_account:
			frappe.throw("Setup Travel/Training Accounts in HR Accounts Settings")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Travel Claim (" + self.employee_name + "  " + self.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Claim payment against : ' + self.name;
		je.posting_date = self.posting_date
		je.branch = self.branch

		total_amt = flt(self.total_claim_amount) + flt(self.extra_claim_amount)
	
		je.append("accounts", {
				"account": expense_account,
				"reference_type": "Travel Claim",
				"reference_name": self.name,
				"cost_center": cost_center,
				"debit_in_account_currency": flt(total_amt),
				"debit": flt(total_amt),
			})
		
		advance_amt = flt(self.advance_amount)
		bank_amt = flt(self.balance_amount)

		if (self.advance_amount) > 0:
			advance_account = frappe.db.get_single_value("HR Accounts Settings", "employee_advance_travel")
			if not advance_account:
				frappe.throw("Setup Advance to Employee (Travel) in HR Accounts Settings")
			if flt(self.balance_amount) < 0:
				advance_amt = flt(self.total_claim_amount)

			je.append("accounts", {
				"account": advance_account,
				"party_type": "Employee",
				"party": self.employee,
				"reference_type": "Travel Claim",
				"reference_name": self.name,
				"cost_center": cost_center,
				"credit_in_account_currency": advance_amt,
				"credit": advance_amt,
			})


		if flt(self.balance_amount) < 0:
			bank_amt = flt(self.total_claim_amount)
		
		je.append("accounts", {
				"account": expense_bank_account,
				"reference_type": "Travel Claim",
				"reference_name": self.name,
				"cost_center": cost_center,
				"credit_in_account_currency": bank_amt,
				"credit": bank_amt,
			})

		je.insert()
	
		#Set a reference to the claim journal entry
		self.db_set("claim_journal", je.name)
	
	##
	# Update the claim reference on travel authorization
	##
	def update_travel_authorization(self):
		ta = frappe.get_doc("Travel Authorization", self.ta)
		ta.db_set("travel_claim", self.name)

	##
	# Allow only approved authorizations to be submitted
	##
	def check_status(self):
		if self.supervisor_approval == 1 and self.hr_approval == 1:
			pass
		else:
			frappe.throw("Both Supervisor and HR has to approve to submit the travel claim")
	
	##
	# Allow only approved authorizations to be submitted
	##
	def check_approval(self):
		if self.supervisor_approval == 0 and self.hr_approval == 1:
			frappe.throw("Supervisor has to approve the claim before HR")
	
	##
	#Ensure the dates are consistent
	##
	def validate_dates(self):
		if self.ta_date > self.posting_date:
			frappe.throw("The Travel Claim Date cannot be earlier than Travel Authorization Date")

	##
	# Allow only the approver to submit the document
	##
	def validate_submitter(self):
		hr_role = frappe.db.get_value("UserRole", {"parent": frappe.session.user, "role": "HR User"}, "role")
		if not hr_role:
			frappe.throw("Only a HR User can submit this document")

	##
	# Send notification to the supervisor / employee
	##
	def sendmail(self, to_email, subject, message):
		email = frappe.db.get_value("Employee", to_email, "user_id")
		if email:
			try:
				frappe.sendmail(recipients=email, sender=None, subject=subject, message=message)
			except:
				pass


