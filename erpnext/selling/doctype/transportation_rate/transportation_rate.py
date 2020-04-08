# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TransportationRate(Document):
	def validate(self):
		if self.to_distance < self.from_distance:
			frappe.throw("To Distance cannot be less than From Distance ")

		data = frappe.db.sql("select name from `tabTransportation Rate` where branch = '{0}' and item_sub_group = '{1}' and '{2}' between from_distance and to_distance and '{3}' between from_distance and to_distance and name != '{4}'".format(self.branch, self.item_sub_group, self.from_distance, self.to_distance, self.name))
		if data:
			frappe.throw("Transportation rate for given details already exist")
