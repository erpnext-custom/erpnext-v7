# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class TargetEntrySheet(Document):
	 def validate(self):
		doc = frappe.get_doc("Project", self.project)
               	self.activity_weightage = doc.physical_progress_weightage
                self.ga_weightage = doc.parent_weightage
		wtg = flt(self.percent_completed)
		per = frappe.db.sql(""" select percent_completed as percent_completed from `tabTarget Entry Sheet` 
			where project = "{0}" and docstatus <= 1 and to_date < '{1}' order by to_date desc limit 1
		""".format(self.project, self.from_date), as_dict = 1)
		#frappe.msgprint("{0}".format(per[0].percent_completed))
		if per:
			wtg = flt(self.percent_completed) - flt(per[0].percent_completed)
		self.percent_completed_overall = round(flt(wtg)/100 * flt(self.activity_weightage), 9)
		self.percent_completed_overall_gi = round(flt(self.percent_completed_overall)/100 * flt(self.ga_weightage), 9)
