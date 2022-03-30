# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class RTSProjects(Document):
	def validate(self):
		self.calculate_initial_amount()
		self.calculate_addition_amount()
		self.calculate_substitution_amount()
		self.rebate_amount = flt(self.rebate)
		if self.rebate_in_percent:
			if flt(self.rebate) > 100:
				frappe.throw("Rebate % Cannot Exceed 100%", title = 'Wrong Input')
				self.rebate = 0.0
			self.rebate_amount = flt(self.rebate) * 0.01 * flt(self.initial_amount)
		
		self.total_amount = flt(self.initial_amount) - flt(self.rebate_amount, 2) + flt(self.addition_amount) + flt(self.substitute_amount)
		self.after_rebate = flt(self.initial_amount) - flt(self.rebate_amount, 2)
		if 0 >= self.total_amount:
			frappe.throw("Total Amount Cannot be Zero")
	
	def get_boq_lists(self):
		result = frappe.db.sql("""
			select boq_item.name as ref_name, boq_item.boq_code, boq_item.item, boq_item.uom, 
			boq_item.is_group, boq_item.ref_type, boq_item.quantity as qty, 
			boq_item.balance_quantity, boq_item.rate, boq_item.remarks
                        from  `tabBOQ` boq, `tabBOQ Item` boq_item
                        where boq.name = boq_item.parent and boq.project = '{0}' and 
			boq_item.quantity != boq_item.balance_quantity
                        and boq.docstatus = 1 order by boq.name, boq_item.idx asc """.format(self.project), as_dict = 1)
		self.set('rts_addition_item', [])
		self.set('rts_substitution_item', [])
		self.set('rts_boq_item', [])
		for d in result:
			d.quantity = flt(d.qty) - flt(d.balance_quantity)
			d.amount = flt(d.quantity) * flt(d.rate)
			if d.ref_type == "BOQ Addition":
				row = self.append('rts_addition_item', {})

			elif d.ref_type == "BOQ Substitution": 
				row = self.append('rts_substitution_item', {})
			
			else: 
				d.ref_type = "BOQ"
				row = self.append('rts_boq_item', {})
			row.update(d)

	def calculate_initial_amount(self):
		initial_amount = total_amount = 0.0
		for a in self.rts_boq_item:
			self.check_duplicate_entries(a)
			if a.is_group:
				a.quantity = a.rate = a.amount = 0.0
			else:
				if flt(a.quantity) <= 0 or flt(a.rate) <= 0:
					frappe.throw("Rate/Quantity Cannot be Zero at Index '{0}'".format(a.idx), title="Initial BOQ")
				
				else:
					a.amount = flt(a.quantity) * flt(a.rate)
			initial_amount += flt(a.amount)
		self.initial_amount = flt(initial_amount)

	def calculate_addition_amount(self):
                addition_amount  =  total_amount = 0.0
                for a in self.rts_addition_item:
			self.check_duplicate_entries(a)
                        if a.is_group:
                                a.quantity = a.rate = a.amount = 0.0
                        else:
                                if flt(a.quantity) <= 0 or flt(a.rate) <= 0:
                                        frappe.throw("Rate/Quantity Cannot be Zero at Index '{0}' ".format(a.idx), title="Addition/Extra Item")

                                else:
                                        a.amount = flt(a.quantity) * flt(a.rate)
                        addition_amount += flt(a.amount)
                self.addition_amount = flt(addition_amount)


	def calculate_substitution_amount(self):
                substitute_amount  =  total_amount = 0.0
                for a in self.rts_substitution_item:
			self.check_duplicate_entries(a)
                        if a.is_group:
                                a.quantity = a.rate = a.amount = 0.0
                        else:
                                if flt(a.quantity) <= 0 or flt(a.rate) <= 0:
                                        frappe.throw("Rate/Quantity Cannot be Zero at Index '{0}'".format(a.idx), title = "Substitution Item")

                                else:
                                        a.amount = flt(a.quantity) * flt(a.rate)
                        substitute_amount += flt(a.amount)
                self.substitute_amount = flt(substitute_amount)
		
	

	def check_duplicate_entries(self, item):
		found = []
		to_remove = []
		if item.ref_name in found:
			to_remove.append(item)
		else:
			found.append(item)
		[self.remove(d) for d in to_remove]	

