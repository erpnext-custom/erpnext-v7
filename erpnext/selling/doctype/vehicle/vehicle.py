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
		if self.common_pool == 0 and frappe.db.exists("Load Request", {"load_status":"Queued", "vehicle":self.name}):
			frappe.throw("Not allow to uncheck Common Pool as the vehicle is already registered in Queue")

		if frappe.db.exists("Transport Request", {"approval_status":"Approved", "vehicle_no":self.name}):
			frappe.db.sql("Update `tabTransport Request` set common_pool = '{0}', self_arranged = '{1}' where vehicle_no = '{2}' and approval_status = 'Approved'".format(self.common_pool, self.self_arranged, self.name))
