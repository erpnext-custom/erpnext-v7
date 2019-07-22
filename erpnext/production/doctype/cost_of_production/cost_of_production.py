# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint

class CostofProduction(Document):
	def validate(self):
		self.check_cop_rate()

	def on_update(self):
		self.check_duplicate_entries()
		self.check_duplicate_settings()

	def check_cop_rate(self):
		for a in self.item_rates:
			if not flt(a.cop_amount) > 0:
				frappe.throw("COP Rate should be greater than 0 for <b>" + str(a.item_sub_group) + "</b>")

	def check_duplicate_entries(self):
		branches = frappe.db.sql("select branch, count(branch) as num from `tabCOP Branch` where parent = %s group by branch having num > 1", self.name, as_dict=1)
		for a in branches:
			frappe.throw("Branch <b>" + str(a.branch) + "</b> has been defined more than once")

		cops = frappe.db.sql("select item_code, count(item_code) as num from `tabCOP Rate Item` where parent = %s group by item_code having num > 1", self.name, as_dict=1)
		for a in cops:
			frappe.throw("Item <b>" + str(a.item_code) + "</b> has been defined more than once")

	def check_duplicate_settings(self):
		#Check branch duplicate
		item_list = []
		for a in self.item_rates:
			item_list.append(a.item_code)

		branch_list = [str(d.branch) for d in self.get("item_branch")]
		branch_list.append(str("DUMMY"))

		for a in frappe.db.sql("""
				select a.branch, b.name 
				from `tabCOP Branch` a, `tabCost of Production` b 
				where a.parent = b.name 
				and b.name != '{0}'
				and a.branch in {1} 
				and (
					('{2}' between b.from_date and b.to_date) or 
					('{3}' between b.from_date and b.to_date) or  
					('{2}' > b.from_date and '{3}' < b.to_date) or 
					('{2}' < b.from_date and '{3}' > b.to_date)
				)
			""".format(self.name, tuple(branch_list), self.from_date, self.to_date), as_dict=1):
			#check for Item duplicate
			doc = frappe.get_doc("Cost of Production", a.name)
			for b in doc.item_rates:
				if b.item_code in item_list:
					frappe.throw("<b>"+str(b.item_code)+"</b> already defined for the same period in <b>"+str(frappe.get_desk_link(self.doctype, a.name))+"</b>")

@frappe.whitelist()
def get_cop_amount(cop, branch, posting_date, item_code):
	if not cop or not branch or not posting_date or not item_code:
		frappe.throw("COP, Branch, Item Code and Posting Date are mandatory")
	cop_amount = frappe.db.sql("select cop_amount from `tabCOP Rate Item` where parent = %s and item_code = %s", (cop, item_code), as_dict=1)
	return cop_amount and flt(cop_amount[0].cop_amount) or 0.0


