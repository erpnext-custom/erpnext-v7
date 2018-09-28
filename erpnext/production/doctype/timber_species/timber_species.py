# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TimberSpecies(Document):
	def autoname(self):
		self.species = self.species.strip()
		self.check_duplicate(self.species.lower())

	def validate(self):
		pass

	def check_duplicate(self, species):
		for a in frappe.db.sql("select name from `tabTimber Species` where LOWER(name) = %s", species, as_dict=1):
			frappe.throw("Species {0} already created".format(a.name))


