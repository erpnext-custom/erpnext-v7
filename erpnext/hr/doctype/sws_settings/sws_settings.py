# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class SWSSettings(Document):
	def validate(self):
		self.validate_plans()

	def validate_plans(self):
		immediate 	 = [i.relation for i in self.immediate]
		nonimmediate = [i.relation for i in self.nonimmediate]
		all 		 = immediate + nonimmediate
  
		if len(all) != len(set(all)):
			for i in self.immediate:
				for n in self.nonimmediate:
					if i.relation == n.relation:
						frappe.throw(_("Relationship <b>{}</b> cannot be part of both the plans").format(i.relation))
