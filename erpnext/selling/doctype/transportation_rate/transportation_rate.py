# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime

class TransportationRate(Document):
	def validate(self):
		if self.to_distance < self.from_distance:
			frappe.throw("To Distance cannot be less than From Distance")
		
		if self.to_date < self.from_date:
			frappe.throw("From Date cannot be after To Date")

		if not self.location:
			cond = " and (location is null or location = '')"
		else:
			cond = " and location = '{0}'".format(self.location)

		check_to_date = frappe.db.sql( """
			select name, from_date, to_date from `tabTransportation Rate` where
			branch = '{0}' and item_sub_group = '{1}'
			and '{2}' between from_date and to_date
			and '{3}' between from_distance and to_distance
			{4} and name != '{5}'
		""".format(self.branch, self.item_sub_group, self.from_date, self.from_distance, cond, self.name), as_dict=True)
		
		if check_to_date:
			frappe.msgprint("Transportation rate with ID: {0} has already defined rate starting from {1} till {2})".format(check_to_date[0].name, datetime.strptime(str(check_to_date[0].from_date),'%Y-%m-%d').strftime('%d-%m-%Y'), datetime.strptime(str(check_to_date[0].to_date),'%Y-%m-%d').strftime('%d-%m-%Y')))
			frappe.throw("Try From Date after {0}".format(datetime.strptime(str(check_to_date[0].to_date),'%Y-%m-%d').strftime('%d-%m-%Y')))
	