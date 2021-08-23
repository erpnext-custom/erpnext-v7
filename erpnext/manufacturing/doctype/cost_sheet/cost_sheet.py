# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words

class CostSheet(Document):
	def validate(self):
		self.check_duplicate_sp()
		self.calculate_cost()

	def check_duplicate_sp(self):
		for a in frappe.db.sql(""" select name
					from `tabCost Sheet`
					where docstatus = 1
					and (
						'{0}' between from_date and to_date 
						or '{1}' between from_date and to_date
						or from_date between '{0}' and '{1}'
						or to_date between '{0}' and '{1}'
					)
					and item = '{2}'
					and name != '{3}'
				""".format(self.from_date, self.to_date, self.item, self.name), as_dict = True):
			if a.name:
				frappe.throw("Sellig price for Item {} is already configured in Cost Sheet {}".format(self.item, a.name))

	def calculate_cost(self):
		self.bom_cost = frappe.db.get_value("BOM", self.bom, "total_cost")
		#frappe.msgprint(str(self.bom_cost))
		manufacturing_overhead = 0.00
		man_overhead_percent = frappe.db.get_single_value("Manufacturing Settings","labour_cost")
		direct_labour_cost = 0.00
		for a in self.items:
			if a.particular == "Labour Cost":
				if man_overhead_percent > 0:
					manufacturing_overhead += flt(man_overhead_percent)/100.00 * flt(a.amount)
				else:
					frappe.throw("Please set percent for Manufacturing Overhead")

			direct_labour_cost += flt(a.amount)
		self.manufacturing_overhead = flt(manufacturing_overhead)

		if self.bom_cost > 0:
			self.prime_cost = flt(direct_labour_cost) + flt(self.bom_cost)
		else:
			frappe.throw("BOM cost cannot be less than 1")

		self.manufacturing_cost = flt(self.prime_cost) + flt(self.manufacturing_overhead)
		
		admin_overhead_percent = frappe.db.get_single_value("Manufacturing Settings","manufacturing_cost")
		self.administrative_and_other_overhead = flt(admin_overhead_percent)/100.00 * flt(self.manufacturing_cost)
		self.production_cost = self.manufacturing_cost + self.administrative_and_other_overhead

		#selling Price
		sp_margin = frappe.db.get_single_value("Manufacturing Settings", "sales_margin")
		self.selling_price = round(((flt(sp_margin) / 100) * flt(self.production_cost)) + flt(self.production_cost))

			
			
