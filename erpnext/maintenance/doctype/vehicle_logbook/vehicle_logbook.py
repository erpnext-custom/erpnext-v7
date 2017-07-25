# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class VehicleLogbook(Document):
	def validate(self):
		for a in self.vlogs:
			for b in self.vlogs:
				if a.date == b.date and a.idx != b.idx:
					frappe.throw("Duplicate Dates in Vehicle Logs in row " + str(a.idx) + " and " + str(b.idx))
		
