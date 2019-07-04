# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, flt, fmt_money, formatdate, nowtime, getdate

class LotList(Document):
	def validate(self):
		#self.calculate_vol()
		pass

	def calculate_vol(self):
		total_vol=0.0
		count = 0
		for item in self.items:
			in_inches = 0
			if self.item_sub_group == "Sawn" or self.item_sub_group == "Block":
				item.volume = (flt(item.length) * flt(item.girth) * flt(item.height)) / 144
			else:
				f = str(item.girth).split(".")
				girth_in_inches = cint(f[0]) * 12
				if len(f) > 1:
					if cint(f[1]) > 11:
						frappe.throw("Inches should be smaller than 12 on row {0}".format(item.idx))
					girth_in_inches += cint(f[1])
				
				item.volume = flt(flt(flt(girth_in_inches * girth_in_inches) * flt(item.length)) / 1809.56) 
					
			total_vol += flt(item.volume)
			count += 1

		self.total_volumne = total_vol
		self.total_pieces = count
