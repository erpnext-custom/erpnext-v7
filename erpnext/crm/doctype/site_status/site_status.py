# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document
from erpnext.crm.doctype.site.site import site_active
from frappe.core.doctype.user.user import send_sms

class SiteStatus(Document):
	def validate(self):
		self.validate_mandatory()
		self.update_user_details()

	def on_submit(self):
		self.update_site()
		self.sendsms()

	def on_cancel(self):
		self.update_site()

	def sendsms(self,msg=None):
		msg2 = ""
		if self.docstatus == 1:
			if self.change_status == "Activate":
				msg2 = "Activation"
			else:
				msg2 = "Deactivation"
			if self.approval_status == "Rejected":
				msg = "Your request for Site {2} is {0}. Tran Ref No {1}. {3}".format(str(self.approval_status).lower(),self.name,msg2,self.rejection_reason)	
			else:
				msg = "Your request for Site {2} is {0}. Tran Ref No {1}".format(str(self.approval_status).lower(),self.name,msg2)	
		mobile_no = frappe.db.get_value("User", self.user, "mobile_no")
		if mobile_no:
			send_sms(mobile_no, msg)

	def update_user_details(self):
		if frappe.db.exists("User Account", self.user):
			doc = frappe.get_doc("User Account", self.user)
			self.full_name = doc.full_name
			self.mobile_no = doc.mobile_no
			self.alternate_mobile_no = doc.alternate_mobile_no

	def validate_mandatory(self):
		self.current_status = "Active" if cint(site_active(self.site)) else "Inactive"
		if self.approval_status == "Rejected" and not self.rejection_reason:
			frappe.throw(_("<b>Rejection Reason</b> is mandatory"))
		elif self.current_status == "Active" and self.change_status == "Activate":
			frappe.throw(_("You cannot <b>{0}</b> a site which is already active").format(self.change_status))
		elif self.current_status == "Inactive" and self.change_status == "Deactivate":
			frappe.throw(_("You cannot <b>{0}</b> a site which is already inactive").format(self.change_status))

	def update_site(self):	
		if self.approval_status == "Rejected":
			return
		elif self.approval_status == "Pending":
			frappe.throw(_("Request cannot be submitted in <b>Pending</b> status"))

		# disable the site
		doc = frappe.get_doc("Site", self.site)
		status = 0
		if self.docstatus == 1:
			status = 1 if self.change_status == "Activate" else 0 
		else:
			status = 0 if self.change_status == "Activate" else 1 

		doc.enabled = status
		doc.save(ignore_permissions=True)
