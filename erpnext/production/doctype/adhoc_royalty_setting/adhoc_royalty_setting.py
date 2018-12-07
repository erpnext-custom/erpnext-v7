# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint

class AdhocRoyaltySetting(Document):
	def validate(self):
		self.convert_to_inches()

	def convert_to_inches(self):
		for a in self.items:
			if not a.from_reading:
				a.from_reading = 0
			if not a.to_reading:
				a.a.to_reading = 0

			in_inches = 0
			f = str(a.from_reading).split(".")
			in_inches = cint(f[0]) * 12
			if len(f) > 1:
				if cint(f[1]) > 11:
					frappe.throw("Inches in 'From Reading' should be smaller than 12 on row {0}".format(a.idx))
				in_inches += cint(f[1])
			a.from_inch = in_inches

			in_inches = 0
			f = str(a.to_reading).split(".")
			in_inches = cint(f[0]) * 12
			if len(f) > 1:
				if cint(f[1]) > 11:
					frappe.throw("Inches in 'To Reading' should be smaller than 12 on row {0}".format(a.idx))
				in_inches += cint(f[1])
			a.to_inch = in_inches


