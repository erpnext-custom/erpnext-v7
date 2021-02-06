# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SliderImages(Document):
	def validate(self):
		# if self.banner:
		# filename = str(self.banner)
		# filename = filename.replace('/private/files/','')
		# doc = frappe.get_doc("File",filename)
		# doc.is_private = 0
		# doc.save()
		pass
