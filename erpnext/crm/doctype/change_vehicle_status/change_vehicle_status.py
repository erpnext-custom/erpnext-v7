# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ChangeVehicleStatus(Document):
	def validate(self):
		current_status = frappe.db.get_value("Vehicle", self.vehicle_no,"vehicle_status")
		if current_status == self.change_status_to:
			frappe.throw("Vehice is already with the same status {0}".format(self.change_status_to))

	def on_submit(self):
		doc = frappe.get_doc("Vehicle", self.vehicle_no)
		doc.db_set("vehicle_status", self.change_status_to)

