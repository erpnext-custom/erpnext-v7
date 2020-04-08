# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, date_diff, nowdate

class VehicleUpdate(Document):
	def validate(self):
		self.validate_vehicle()
		
	def on_submit(self):
		if self.approval_status != "Pending":
			self.update_details()
		else:
			frappe.throw("Change the Approval Status to Approved or Rejected to Submit the document")

	def validate_vehicle(self):
		self.posting_date = getdate(nowdate())

		doc = frappe.get_doc("Vehicle", self.vehicle)

		if doc.vehicle_status != "Active":
			frappe.throw("Not allowed to change details of Vehicle {0} as the status is {1}".format(self.vehicle, doc.vehicle_status))

		if not frappe.db.exists("Vehicle", {"name":self.vehicle, "user":self.user, "docstatus": ("<",2)}):
			frappe.throw("You are not authorized to change status of Vehicle {0}".format(self.vehicle))

	def update_details(self):
		doc = frappe.get_doc("Vehicle", self.vehicle)
		if not self.driver_name or not self.driver_mobile_no:
			frappe.throw("Please provide driver details to update")
		else:
			frappe.db.sql("update `tabVehicle` set drivers_name = '{0}', contact_no = '{1}' where name = '{2}'".format(self.driver_name, self.driver_mobile_no, self.vehicle))
			frappe.db.sql("update `tabTransport Request` set drivers_name = '{0}', contact_no = '{1}' where  vehicle_no = '{2}' and user='{3}' and approval_status = 'Approved'".format(self.driver_name, self.driver_mobile_no, self.vehicle, self.user))

	
	def check_and_update_vehicle_queue(self):
		# Update Vehicle Queuing for Common Pool
		if frappe.db.exists("Load Request", {"vehicle":self.vehicle, "load_status":"Queued", "docstatus": 1, "queuing_date":(">=", self.posting_date)}):
			branch, queuing_date, token = frappe.db.get_value("Load Request", {"vehicle":self.vehicle, "load_status":"Queued", "docstatus":1, "queuing_date":(">=", self.posting_date)}, ["crm_branch", "queuing_date", "token"])
			for a in frappe.db.sql("select name, vehicle, token from `tabLoad Request` where queuing_date='{0}' and crm_branch ='{1}' and token >= '{2}' order by token".format(queuing_date, branch, token), as_dict=True):
				doc = frappe.get_doc("Load Request", a.name)
				if a.vehicle == self.vehicle:
					doc.db_set("load_status", "Cancelled")
					doc.db_set("docstatus", 2)
				else:
					new_token = a.token - 1
					doc.db_set("token", new_token)
