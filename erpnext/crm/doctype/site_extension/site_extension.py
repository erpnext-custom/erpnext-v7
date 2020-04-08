# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, getdate
from frappe.model.document import Document
from erpnext.crm.doctype.site.site import site_active
from frappe.core.doctype.user.user import send_sms

class SiteExtension(Document):
	def validate(self):
		self.validate_mandatory()
		self.validate_extension_date()
		self.update_user_details()

	def after_insert(self):
		#msg = "Your request for Site Extension is Pending Approval. Tran Ref No {0}".format(self.name)
		#self.sendsms(msg)
		pass

	def on_submit(self):
		self.update_site()
		self.sendsms()

	def on_cancel(self):
		self.update_site()

	def update_user_details(self):
		if frappe.db.exists("User Account", self.user):
			doc = frappe.get_doc("User Account", self.user)
			self.full_name = doc.full_name
			self.mobile_no = doc.mobile_no
			self.alternate_mobile_no = doc.alternate_mobile_no

	def sendsms(self,msg=None):
		if self.docstatus == 1:
			if self.approval_status == "Rejected":
				msg = "Your request for Site Extension is {0}. Tran Ref No {1}. {2}".format(str(self.approval_status).lower(),self.name,self.rejection_reason)	
			else:
				msg = "Your request for Site Extension is {0}. Tran Ref No {1}".format(str(self.approval_status).lower(),self.name)	
		mobile_no = frappe.db.get_value("User", self.user, "mobile_no")
		if mobile_no:
			send_sms(mobile_no, msg)

	def validate_mandatory(self):
		if self.approval_status == "Rejected" and not self.rejection_reason:
			frappe.throw(_("Rejection Reason is mandatory"))	
		else:
			if not cint(site_active(self.site)): 
				frappe.throw(_("Extension not permitted as the Site is already deactivated"))	
			
	def validate_extension_date(self):
		self.construction_start_date, self.construction_end_date, site_extension_date = \
			frappe.db.get_value("Site", self.site, ["construction_start_date","construction_end_date","extension_till_date"])

		site_extension_date = site_extension_date if site_extension_date else self.construction_end_date	
		self.construction_end_date = site_extension_date
		if getdate(self.extension_till_date) <= getdate(site_extension_date):
			frappe.throw(_("Extension Till Date should be later to {0}").format(site_extension_date.strftime("%d %B, %Y")))	

	def update_site(self):
		""" extend extension_till_date in Site """
		if self.approval_status == "Rejected":
			return
		elif self.approval_status == "Pending":
			frappe.throw(_("Request cannot be submitted in Pending status"))
		#elif not self.extension_approval_document:
		#	frappe.throw(_("Please attach Extension Approval Document"))	

		doc = frappe.get_doc("Site", self.site)
		extension_till_date         = self.extension_till_date
		extension_approval_document = self.extension_approval_document
		if self.docstatus == 2:
			latest = frappe.db.sql("""select extension_till_date, extension_approval_document
				from `tabSite Extension`
				where user = "{user}"
				and site = "{site}"
				and approval_status = "{approval_status}"
				and docstatus = 1
				order by extension_till_date desc 
				limit 1
			""".format(user=self.user, site=self.site, approval_status=self.approval_status))
			if latest:
				extension_till_date         = latest[0][0]
				extension_approval_document = latest[0][1]
			else:
				extension_till_date         = None
				extension_approval_document = None

		doc.extension_till_date         = extension_till_date
		doc.extension_approval_document = extension_approval_document
		doc.save(ignore_permissions = True)
