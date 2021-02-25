# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TargetEntrySheet(Document):
	def validate(self):
		doc = frappe.get_doc("Project", self.project)
		self.activity_weightage = doc.physical_progress_weightage
		self.ga_weightage = doc.parent_weightage
