# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, date_diff, nowdate
from frappe.core.doctype.user.user import send_sms

class TransportRequest(Document):
	def validate(self):
		#remove space in vehicle no
		v_no = self.vehicle_no
		self.vehicle_no = v_no.replace(" ","")
		
		#make status same with approval Status
		self.status = self.approval_status

		self.map_user_transport()
		self.request_date = getdate(nowdate())
		self.validate_vehicle()

	def map_user_transport(self):
		#if not self.user:
			#account_type = frappe.db.get_value("User", frappe.session.user, "account_type")
			#if account_type == "CRM":
			#	self.user = frappe.session.user
			
		if self.common_pool:
			if not self.transporter_name:
				self.transporter_name = frappe.db.get_value("User", self.user, "first_name")

	def validate_vehicle(self):
		vehicle = self.vehicle_no
		self.vehicle_no = vehicle.upper()
		vehicle_dtl = frappe.db.sql("select name, user from `tabTransport Request` where vehicle_no='{0}' and approval_status in ('Pending', 'Approved') and name!= '{1}'".format(self.vehicle_no, self.name), as_dict = True)
		if vehicle_dtl:
			for a in vehicle_dtl:
				r_user = a.user
			frappe.throw("Vehicle {0} is already in Transport Request with User {1}".format(self.vehicle_no, r_user))

		if frappe.db.exists("Vehicle", self.vehicle_no):
			docv = frappe.get_doc("Vehicle", self.vehicle_no)
			if docv.vehicle_status != "Deregistered" and docv.user:
				frappe.throw("Vehicle is already registered with status {0}".format(docv.vehicle_status))
			if self.approval_status == "Approved" and self.docstatus == 1:
				docv.db_set('user', self.user)

		if not self.common_pool:
			if not self.self_arranged:
				frappe.throw("The transport request should be either Common Pool or Self Owned")
		

	def on_submit(self):
#		if not self.registration_document:
#			frappe.throw("Please attach vehicle registration document")
		#if self.owner == "Spouse":
		#	if not self.marriage_certificate:
		#		frappe.throw("You must attach MC copy as the vehicle is registered on your spouse name")
			
		if self.approval_status == "Pending":
			frappe.throw("Change the Approval Status other than Pending to submit ")

		if self.approval_status == "Approved":
			self.create_transporter_vehicle()
		self.sendsms()

	def sendsms(self,msg=None):
		if self.docstatus == 1:
			msg = "Your request for Transport Registration is {0}. Tran Ref No {1}".format(str(self.approval_status).lower(),self.name)
		mobile_no = frappe.db.get_value("User", self.user, "mobile_no")
		if mobile_no:
			send_sms(mobile_no, msg)

	def create_transporter_vehicle(self):
		u_mobile_no = frappe.db.get_value("User", {"login_id":self.user}, "mobile_no")
		transporter = ""
		if self.common_pool:
			if not frappe.db.exists("Transporter", {"transporter_id": self.user, "docstatus": ("<",2)}):
				doc = frappe.new_doc("Transporter")
				doc.transporter_name = self.transporter_name
				doc.transporter_id = self.user
				doc.mobile_no = u_mobile_no
				doc.user = self.user		
				doc.submit()				
	
			transporter, enabled = frappe.db.get_value("Transporter", {"transporter_id": self.user}, ["transporter_name", "enabled"])

		if frappe.db.exists("Vehicle", self.vehicle_no):
			v_doc = frappe.get_doc("Vehicle", self.vehicle_no)
			v_doc.db_set("vehicle_capacity", self.vehicle_capacity)
			v_doc.db_set("common_pool", self.common_pool)
			v_doc.db_set("self_arranged", self.self_arranged)
			v_doc.db_set("drivers_name", self.drivers_name)
			v_doc.db_set("owner_cid", self.owner_cid)
			v_doc.db_set("contact_no", self.contact_no)
			v_doc.db_set("user", self.user)
			v_doc.db_set("vehicle_status", "Active")
			v_doc.save(ignore_permissions = True)	
		else:	
			v_doc = frappe.new_doc("Vehicle")
			v_doc.vehicle_no = self.vehicle_no
			v_doc.common_pool = self.common_pool
			v_doc.self_arranged = self.self_arranged
			v_doc.vehicle_capacity = self.vehicle_capacity
			v_doc.drivers_name = self.drivers_name
			v_doc.owner_cid = self.owner_cid
			v_doc.contact_no = self.contact_no
			v_doc.user = self.user
			v_doc.submit()
						
