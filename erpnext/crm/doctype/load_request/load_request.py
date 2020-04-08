# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, date_diff, nowdate
import datetime

class LoadRequest(Document):
	def validate(self):
		self.update_default_values()
		self.validate_vehicle()

	def update_default_values(self):
		self.crm_branch = "Sha Sand and Stone Unit"
		if self.crm_branch and self.vehicle and self.user:
			if self.load_status != "Cancelled":
				self.load_status = "Queued"
			else:
				self.docstatus = 2

	def on_submit(self):
		pass

	def on_cancel(self):
		pass
	
	def validate_vehicle(self):
		if not frappe.db.exists("Vehicle", {"name": self.vehicle, "user":self.user, "vehicle_status":"Active"}):
			frappe.throw("Vehicle {0} not allowed to request load. Please check vehicle status".format(self.vehicle))

		if self.load_status != "Cancelled":
			if frappe.db.exists("Load Request", {"vehicle":self.vehicle, "crm_branch": self.crm_branch, "load_status": "Queued"}):
				frappe.throw("Vehicle {0} is already in Load Queue".format(self.vehicle))

		if frappe.db.exists("tabDelivery Confirmation", {"vehicle":self.vehicle, "confirmation_status": "In Transit"}):

			for a in frappe.db.sql("select customer, delivery_note, branch from `tabDelivery Confirmation` where vehicle = '{0}' and confirmation_status = 'In Transit' limit 1".format(self.vehicle)):
				frappe.throw("Vehicle {0} Delivery Confirmation is pending for DN {1} under {2}".format(self.vehicle, a.delivery_note, a.branch))

		if self.vehicle:
			vehicle_capacity = frappe.db.get_value("Vehicle", self.vehicle, "vehicle_capacity")
			if not vehicle_capacity or vehicle_capacity < 1:
				frappe.throw("Vehicle Capacity is Mandatory and greater than 0")
			else:
				self.vehicle_capacity = vehicle_capacity
			
		self.requesting_date_time = datetime.datetime.now() #datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		for a in frappe.db.sql("select max(token) as token from `tabLoad Request` where vehicle_capacity = '{0}'".format(vehicle_capacity), as_dict=True):
			self.token = cint(a.token) + 1
