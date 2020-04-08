# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Vehicle(Document):
	def autoname(self):
		self.name = self.vehicle_no.replace(" ", "").upper()

#	def validate(self):
#		self.vehicle_no = self.vehicle_no.upper()
