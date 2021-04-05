# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class ActivityTasks(Document):
	def validate(self):
		#x = make_autoname(str(self.task) + '.####')
		#if self.is_group:
                #	self.name = x
		if self.is_group:
			self.name = self.name + self.task
