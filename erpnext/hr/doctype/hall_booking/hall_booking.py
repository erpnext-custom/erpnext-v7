# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class HallBooking(Document):
	def validate(self):
		query = "select customer, from_date, to_date, hall_type from `tabHall Booking` \
			where from_date between \'" + str(self.from_date) + "\'and \'" + str(self.to_date) + "\' and \
			to_date between \'" + str(self.from_date) + "\'and \'" + str(self.to_date) + "\' and \
			hall_type= \'" + str(self.hall_type) + "\' and docstatus = 1"
		data = frappe.db.sql(query, as_dict=True)
		if data:
			frappe.throw("Hall type <b>{0}</b> has been already booked by <b>{1}</b> from <b>{2}</b> till <b>{3}</b>".format(data[0].hall_type, data[0].customer, data[0].from_date, data[0].to_date))
