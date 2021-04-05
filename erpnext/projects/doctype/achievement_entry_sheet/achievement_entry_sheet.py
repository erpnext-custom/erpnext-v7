# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class AchievementEntrySheet(Document):
	def validate(self):
		doc = frappe.get_doc("Project", self.project)
                self.activity_weightage = doc.physical_progress_weightage
                self.ga_weightage = doc.parent_weightage	
		self.percent_completed_overall = round(flt(self.percent_completed)/100 * flt(self.activity_weightage), 9)	
		self.percent_completed_overall_gi = round((self.percent_completed_overall)/100 * flt(self.ga_weightage),9)
