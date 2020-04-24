# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Vehicle(Document):
	def autoname(self):
		self.name = self.vehicle_no.replace(" ", "").upper()

	def validate(self):
		if self.vehicle_no:
			vehicle_number = self.vehicle_no
			vehicle_last_four_digit = vehicle_number[-4:]
			check = 0
			for a in frappe.db.sql("select name, vehicle_status from `tabVehicle` where name like '%{0}'".format(vehicle_last_four_digit), as_dict=True):
				frappe.msgprint("Vehicle with similar number " + a.name + " status " + a.vehicle_status + " is already registered")
				check += 1
			if check > 0:
				frappe.throw("There are vehicle already registered with similar number to {0}".format(self.vehicle_no))

	def on_update_after_submit(self):
		if self.common_pool == 0 and frappe.db.exists("Load Request", {"load_status":"Queued", "vehicle":self.name}):
			frappe.throw("Not allow to uncheck Common Pool as the vehicle is already registered in Queue")

		if frappe.db.exists("Transport Request", {"approval_status":"Approved", "vehicle_no":self.name}):
			frappe.db.sql("Update `tabTransport Request` set common_pool = '{0}', self_arranged = '{1}' where vehicle_no = '{2}' and approval_status = 'Approved'".format(self.common_pool, self.self_arranged, self.name))
