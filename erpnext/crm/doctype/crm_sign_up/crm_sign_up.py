# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.core.doctype.user.user import crm_sign_up, send_pin, validate_mobile_no, send_sms
from frappe.model.mapper import get_mapped_doc

class CRMSignup(Document):
	def validate(self):
		self.check_duplicates()
		self.validate_defaults()

	def on_submit(self):
		self.validate_mandatory()
		self.create_user_account()
		self.create_user_request()
		frappe.msgprint(_("User Account created successfully"))

	def create_user_account(self):
		create_pin(self.full_name, self.cid, self.mobile_no, self.pin)
		user = frappe.get_doc({
			"doctype":"User",
			"account_type": "CRM",
			"first_name": self.full_name,
			"username": self.cid,
			"login_id": self.cid,
			"mobile_no": self.mobile_no,
			"alternate_mobile_no": self.alternate_mobile_no,
			"email": self.email_id,
			"enabled": 1,
			"new_password": self.pin,
			"user_type": "System User",
			"api_key": frappe.generate_hash(length=15),
			"api_secret": frappe.generate_hash(length=15),
			"user_roles": [{"role": "CRM User"}]
		})
		user.flags.ignore_permissions = True
		user.save()

	def create_user_request(self):
		#create user request for CID
		doc = frappe.new_doc("User Request")
		doc.user = self.cid
		doc.new_cid = self.cid
		doc.request_type = "Registration"
		doc.request_category = "CID Details"
		doc.approval_status = "Approved"
		doc.flags.ignore_permissions = True
		doc.send_sms = self.send_sms
		doc.sms_content = "You are successfully registered for NRDCL online services. You can now login with your registered CID# {} and PIN {}".format(self.cid,self.pin)
		doc.save()

		''' attach documents '''
		target_doc = None
		def set_missing_values(source, target):
			target.attached_to_doctype = "User Request"
			target.attached_to_name = doc.name

		if doc:
			for i in frappe.db.get_all("File", "name", {"attached_to_doctype": self.doctype, "attached_to_name": self.name}):
				attachment = get_mapped_doc("File", i.name, {
						"File": {
							"doctype": "File",
						},
				}, target_doc, set_missing_values)
				attachment.save(ignore_permissions=True)
		doc.submit()

	def check_duplicates(self):
		for i in frappe.db.get_all("User Account", "name", {"name": self.cid}):
			frappe.throw(_("User Account already exists ref# {}").format(frappe.get_desk_link("User Account", i.name)))

	def validate_defaults(self):
		self.full_name = str(self.full_name).strip()
		self.cid  = str(self.cid).strip()
		self.mobile_no = str(self.mobile_no).strip()
		self.pin = str(self.pin).strip()

		validate_mobile_no(self.mobile_no)
		if self.alternate_mobile_no:
			validate_mobile_no(self.alternate_mobile_no)

	def validate_mandatory(self):
		if not self.cid_front:
			frappe.throw(_("CID Front Image is mandatory"))

def create_pin(full_name, login_id, mobile_no, pin):
	salt = frappe.generate_hash()
	full_name = str(full_name).strip()
	login_id  = str(login_id).strip()
	mobile_no = validate_mobile_no(mobile_no)

	frappe.db.sql("""insert into __PIN (full_name,login_id,mobile_no,pin,salt,owner,creation)
		values (%(full_name)s, %(login_id)s, %(mobile_no)s, password(concat(%(pin)s, %(salt)s)), %(salt)s, %(full_name)s,now())
		on duplicate key update
			pin=password(concat(%(pin)s, %(salt)s)), salt=%(salt)s""",
		{ 'full_name': full_name, 'login_id': login_id, 'mobile_no': str(mobile_no)[-8:], 'pin': pin, 'salt': salt })
