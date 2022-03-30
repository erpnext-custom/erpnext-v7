# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LoadRequestEditor(Document):
	def on_submit(self):
		for a in self.items:
			if a.new_requesting_date_time and a.new_requesting_date_time != "" and a.new_requesting_date_time != None:
				lr = frappe.get_doc("Load Request", a.load_request_id)
				lr.db_set("requesting_date_time",a.new_requesting_date_time)
		frappe.msgprint("Queue Updated.")

	def get_queue(self):
		if not self.branch:
			frappe.throw("Please select Branch")
		if not self.vehicle_capacity:
			frappe.throw("Please select Vehicle Capacity")
		if not self.no_of_vehicles or self.no_of_vehicles == 0:
			limit = ""
		else:
			limit = " limit {}".format(self.no_of_vehicles)
		query = "select vehicle, name as load_request_id, requesting_date_time from `tabLoad Request` where load_status = 'Queued' and vehicle_capacity = {} and crm_branch = '{}' order by requesting_date_time asc {}".format(self.vehicle_capacity, self.branch, limit)
		entries = frappe.db.sql(query, as_dict=True)
		if not entries:
			frappe.msgprint("No Vehicles in Queue.")
		self.set('items', [])
		for d in entries:
			row = self.append('items', {})
			row.update(d)


