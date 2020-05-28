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
		pass

	def on_update_after_submit(self):
		self.update_transport_request()
		if self.common_pool == 0 and frappe.db.exists("Load Request", {"load_status":"Queued", "vehicle":self.name}):
			frappe.throw("Not allow to uncheck Common Pool as the vehicle is already registered in Queue")

	def update_transport_request(self):
		self.vehicle_no = self.vehicle_no.upper()
		vehicle = self.vehicle_no
		cond = "upper(vehicle_no)"
		for x in [' ', '+', '-', '(', ')', '/', '#']:
			vehicle = vehicle.replace(x, '')
			cond = "replace({},'{}','')".format(cond, x)
		cond += " like '%{}%'".format(vehicle)

		for a in frappe.db.sql("""select name from `tabTransport Request` 
				       where {}
				       and approval_status in ('Pending', 'Approved') 
				       and docstatus != 2
				      """.format(cond, self.name), as_dict = True):
			frappe.db.sql("Update `tabTransport Request` set common_pool = '{0}', self_arranged = '{1}', vehicle_capacity = '{2}' where name = '{3}'".format(self.common_pool, self.self_arranged, self.vehicle_capacity, a.name))
