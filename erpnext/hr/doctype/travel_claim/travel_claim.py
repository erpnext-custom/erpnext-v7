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
		self.validate_dates()
		self.check_approval()
		self.update_travel_authorization()
		employee = frappe.db.get_value("Employee", self.employee, "user_id")

		if self.supervisor_approval and (frappe.session.user == self.owner or frappe.session.user == employee):
			frappe.throw("Cannot edit once approved by supervisor")

		if frappe.session.user == self.owner or frappe.session.user == employee:
			self.db_set("claim_status", "")
			self.sendmail(frappe.db.get_value("Employee", {"user_id": self.supervisor}, "name"), "Travel Claim Submitted", str(self.employee_name) + " has requested you to verify and sign a travel claim")
		elif self.claim_status == "Rejected by Supervisor":
			self.sendmail(self.employee, "Travel Claim Rejected by Supervisor" + str(self.name), "Following remarks has been added by the supervisor: \n" + str(self.reason))
		elif self.claim_status == "Rejected by HR":
			self.sendmail(self.employee, "Travel Claim Rejected by HR" + str(self.name), "Following remarks has been added from HR: \n" + str(self.reason))

		if frappe.session.user == self.supervisor and self.supervisor_approval:
			self.db_set("supervisor_approved_on", nowdate())
		
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


	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		cost_center = frappe.db.get_value("Division", self.division, "cost_center")
		if not self.division:
			frappe.throw("Employee has not been assigned a division")
		if not cost_center:
			frappe.throw("No Cost Center has been assigned against " + str(self.division))
		
		gl_account = ""	
		if self.travel_type == "Travel":
			if self.place_type == "In-Country":
				gl_account =  "Travel-Local - SMCL"
			else:
				gl_account = "Travel-Foreign - SMCL"
		elif self.travel_type == "Training":
			if self.place_type == "In-Country":
				gl_account = "Training-Incountry - SMCL"
			else:
				gl_account = "Training-Excountry - SMCL"
		else:
			if self.place_type == "In-Country":
				gl_account = "In-Country Seminars / Workshops/Meeting - SMCL"
			else:
				gl_account = "Out-Country Seminars / Workshops/Meeting - SMCL"
		
		if gl_account == "":
			frappe.throw("Incorrect GL Account. Kindly check your travel purpose and submit again")

		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Travel Claim (" + self.employee_name + "  " + self.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Claim payment against : ' + self.name;
		je.posting_date = self.posting_date

		total_amt = flt(self.total_claim_amount) + flt(self.extra_claim_amount)
	
		je.append("accounts", {
				"account": gl_account,
				"reference_type": "Travel Claim",
				"reference_name": self.name,
				"cost_center": cost_center,
				"debit_in_account_currency": flt(total_amt),
				"debit": flt(total_amt),
			})
		
		je.append("accounts", {
				"account": "Sundry Creditors - Employee - SMCL",
				"party_type": "Employee",
				"party": self.employee,
				"reference_type": "Travel Claim",
				"reference_name": self.name,
				"cost_center": cost_center,
				"debit_in_account_currency": flt(total_amt),
				"debit": flt(total_amt),
			})
		
		je.append("accounts", {
				"account": "Sundry Creditors - Employee - SMCL",
				"party_type": "Employee",
				"party": self.employee,
				"reference_type": "Travel Claim",
				"reference_name": self.name,
				"cost_center": cost_center,
				"credit_in_account_currency": flt(total_amt),
				"credit": flt(total_amt),
			})
		
		advance_amt = flt(self.advance_amount)
		bank_amt = flt(self.balance_amount)

		if (self.advance_amount) > 0:
			if flt(self.balance_amount) < 0:
				advance_amt = flt(self.total_claim_amount)

			je.append("accounts", {
				"account": "Advance to Employee-Travel - SMCL",
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
				"account": "Bank of Bhutan Ltd - 100891887 - SMCL",
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
			frappe.sendmail(recipients=email, sender=None, subject=subject, message=message)


