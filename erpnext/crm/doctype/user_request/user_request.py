# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, get_datetime
from frappe.model.document import Document
from frappe.core.doctype.user.user import validate_mobile_no
from frappe.model.mapper import get_mapped_doc
from frappe.core.doctype.user.user import send_sms

fields = {"CID Details": ["cid", "cid_file_front", "cid_file_back", "date_of_issue", "date_of_expiry"], 
		"Address Details": ["address_type", "address_line1", "address_line2", "dzongkhag", "gewog", "pincode"],
		"Contact Details": ["first_name", "last_name", "email_id", "mobile_no", "alternate_mobile_no"], 
		"Bank Details": ["financial_institution", "financial_institution_branch", "account_number"]}

class UserRequest(Document):
	def validate(self):
		self.validate_mandatory()
		self.update_user_details()
		self.validate_cid()
		self.validate_mobile_no()
		self.set_old_details()
		self.update_user()

	def after_insert(self):
		#msg = "Your request for update in {0} is Pending Approval.".format(self.request_category)
		#self.sendsms(msg)
		pass

	def on_submit(self):
		self.update_user_account()
		self.sendsms()

	def on_cancel(self):
		""" notify user that cancellation shall have no import on User Account """
		self.update_user()
		self.update_user_account()

	def update_user_details(self):
		if frappe.db.exists("User Account", self.user):
			doc = frappe.get_doc("User Account", self.user)
			self.full_name = doc.full_name
			self.mobile_no = doc.mobile_no
			self.alternate_mobile_no = doc.alternate_mobile_no

	def sendsms(self,msg=None):
		if self.docstatus == 1:
			if self.approval_status == "Approved" and self.request_category == "CID Details" \
				and not frappe.db.exists("User Request", {"name": ("!=",self.name),"user": self.user, \
					"request_category": self.request_category, "docstatus":1, "approval_status": "Approved"}):
				msg = """You are successfully registered for NRDCL online services. 
					You can now login with your registered CID number and PIN received 
					during registration process."""
			else:
				if self.approval_status == "Rejected":
					msg = "Your request for update in {0} is {1}. Tran Ref No {2}. {3}".format(str(self.request_category).lower(), str(self.approval_status).lower(),self.name,self.rejection_reason)
				else:
					msg = "Your request for update in {0} is {1}. Tran Ref No {2}".format(str(self.request_category).lower(), str(self.approval_status).lower(),self.name)
		mobile_no = frappe.db.get_value("User", self.user, "mobile_no")
		if mobile_no and cint(self.send_sms):
			msg = self.sms_content if self.sms_content else msg
			send_sms(mobile_no, msg)

	def set_old_details(self):
		if frappe.db.exists("User Request",{"user": self.user, "name": ("!=", self.name), \
			"request_category": self.request_category, "docstatus": ("!=",2)}):
			self.request_type = "Change Request"
		else:
			self.request_type = "Registration"

		old = get_old_details(self.user)
		if old:
			for i in fields.get(self.request_category):	
				src_prefix  = ""
				dest_prefix = "old_"

				if self.request_category == "Address Details":
					if self.new_address_type == "Billing Address":
						src_prefix = "billing_"
					elif self.new_address_type == "Permanent Address":
						src_prefix = "perm_"

				vars(self)[dest_prefix+i] = old.get(src_prefix+i) 

	def update_user(self):
		if self.request_category == "CID Details":
			user = frappe.get_doc("User", self.user)
			latest = self.get_latest_entry()
			profile_submitted = user.profile_submitted
			profile_verified  = user.profile_verified

			if not self.docstatus:
				profile_submitted = (1 if latest else 0) if self.approval_status == "Rejected" else 1
			elif self.docstatus == 2:
				if not frappe.db.exists("User Request", {"user": self.user, "name": ("!=", self.name), \
						"request_category": "CID Details", "docstatus": 1}):
					profile_submitted = 0
					profile_verified  = 0
			else:
				profile_verified = (1 if latest else 0) if self.approval_status == "Rejected" else 1

			user.profile_submitted = profile_submitted
			user.profile_verified  = profile_verified
			user.save(ignore_permissions=True)

	def validate_cid(self):
		if self.request_category == "CID Details":
			if self.new_date_of_expiry and get_datetime(self.new_date_of_expiry) <= get_datetime(self.new_date_of_issue):
				frappe.throw(_("Date of Expiry cannot be earlier to date of issue"))
		if not frappe.db.exists("User Request",{"user":self.user,"request_category":"CID Details","docstatus":1})\
				and self.request_category != "CID Details":
			frappe.throw(_("You need to submit a copy of CID document first"))

	def validate_mobile_no(self):
		""" validations of mobile number format """
		if self.request_category == "Contact Details" and self.new_mobile_no:
			#validate_mobile_no(self.new_mobile_no)
			validate_mobile_no(self.new_alternate_mobile_no)

	def validate_mandatory(self):
		""" validate mandatory fields for selected request category """
		self.full_name,self.mobile_no,self.alternate_mobile_no = frappe.db.get_value("User", self.user, ["full_name","mobile_no","alternate_mobile_no"])
		fields = {"CID Details": ["cid"], 
				"Address Details": ["address_type", "address_line1", "dzongkhag", "gewog"],
				"Contact Details": ["first_name"], 
				"Bank Details": ["financial_institution", "financial_institution_branch", "account_number"]}
		for i in fields.get(self.request_category):
			fieldname = "new_"+i
			if not self.get(fieldname):
				frappe.throw(_("{0} is mandatory").format(self.meta.get_label(fieldname)))	 

		if self.approval_status == "Rejected" and not self.rejection_reason:
			frappe.throw(_("Rejection Reason cannot be empty"))

	def get_latest_entry(self):
		latest = frappe.db.sql("""
			select *
			from `tabUser Request`
			where user = "{user}"
			and request_category = "{request_category}"
			and approval_status = "Approved"
			and name != "{name}"
			and docstatus = 1
			order by modified desc
			limit 1
		""".format(user=self.user, request_category=self.request_category, name=self.name), as_dict=True)
		return latest[0] if latest else None

	def update_user_account(self):
		""" insert/update the request to User Account """
		target_doc = None
		def set_missing_values(source, target):
			target.attached_to_doctype = "User Account"
			target.attached_to_name = self.user

		if self.approval_status == "Rejected":
			return
		elif self.approval_status == "Pending":
			frappe.throw(_("Request cannot be submitted in <b>Pending</b> status"))

		if not frappe.db.exists('File', {'attached_to_doctype': self.doctype, 'attached_to_name': self.name})\
			and self.request_category == "CID Details":
			frappe.throw(_("Please attach valid copy of CID"))

		if frappe.db.exists("User Account", self.user):
			doc = frappe.get_doc("User Account", self.user)
		else:
			doc = frappe.new_doc("User Account")

		doc.user = self.user
		doc.full_name = self.full_name

		source_doc = self
		latest = None
		if self.docstatus == 2:
			latest = self.get_latest_entry()
			if latest:
				source_doc = latest

		for i in fields.get(self.request_category):	
			src_prefix  = "new_" if latest else ("none_" if self.docstatus == 2 else "new_")
			dest_prefix = ""

			if self.request_category == "Address Details":
				if self.new_address_type == "Billing Address":
					dest_prefix = "billing_"
				elif self.new_address_type == "Permanent Address":
					dest_prefix = "perm_"

			vars(doc)[dest_prefix+i] = source_doc.get(src_prefix+i) 
		doc.save(ignore_permissions=True)

		''' attach documents '''
		if doc and self.docstatus != 2:
			for i in frappe.db.get_all("File", "name", {"attached_to_doctype": self.doctype, "attached_to_name": self.name}):
				attachment = get_mapped_doc("File", i.name, {
						"File": {
							"doctype": "File",
						},
				}, target_doc, set_missing_values)
				attachment.save(ignore_permissions=True)
	
@frappe.whitelist()
def get_old_details(user):
	""" return User Account information """
	doc = None
	if frappe.db.exists("User Account", user):
		doc = frappe.get_doc("User Account", user)
	return doc
