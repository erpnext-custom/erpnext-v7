# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import re

class SWSMembershipItem(Document):
	def autoname(self):
		# doc = frappe.get_doc("SWS Membership", self.parent)
		self.name = self.full_name+"-"+self.relationship+"-"+str(self.employee)
		# pname = frappe.db.sql("select name from `tabSWS Membership Item` where name = '{}'".format(naming_code),as_dict=True)
		# if not pname:
		# 	self.name = naming_code
		# else:
		# 	length = str(naming_code).split("-")
		# 	if len(length) == 3:
		# 		num = int(length[2])
		# 		self.name = naming_code+str(num+1)
		# 	else:
		# 		self.name = naming_code+"-01"

