# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint

class SellingPrice(Document):
	def validate(self):
		self.check_sp_rate()

	def on_update(self):
		self.check_duplicate_entries()

	def check_sp_rate(self):
		for a in self.item_rates:
			if not flt(a.selling_price) > 0:
				frappe.throw("Selling Rate should be greater than 0 for <b>" + str(a.particular) + "</b>")

			if a.price_based_on == "Item":
				a.item_name = frappe.db.get_value("Item", a.particular, "item_group")
			else:
				a.item_name = None

	def check_duplicate_entries(self):
		branches = frappe.db.sql("select branch, count(branch) as num from `tabSelling Price Branch` where parent = %s group by branch having num > 1", self.name, as_dict=1)
		for a in branches:
			frappe.throw("Branch <b>" + str(a.branch) + "</b> has been defined more than once")

		sps = frappe.db.sql("select particular, timber_type, count(particular) as num from `tabSelling Price Rate` where parent = %s group by particular, timber_type having num > 1", self.name, as_dict=1)
		for a in sps:
			if a.timber_type:
				frappe.throw("<b>" + str(a.particular) + "/" + str(a.timber_type) + "</b> has been defined more than once")
			else:
				frappe.throw("<b>" + str(a.particular) + "</b> has been defined more than once")

@frappe.whitelist()
def get_cop_amount(cop, branch, posting_date, item_code):
	if not cop or not branch or not posting_date or not item_code:
		frappe.throw("COP, Branch, Item Code and Posting Date are mandatory")
	item_sub_group = frappe.db.get_value("Item", item_code, "item_sub_group")
	if not item_sub_group:
		frappe.db.sql("No Item Sub Group Assigned")
	cop_amount = frappe.db.sql("select cop_amount from `tabCOP Rate Item` where parent = %s and item_sub_group = %s", (cop, item_sub_group), as_dict=1)
	return cop_amount and flt(cop_amount[0].cop_amount) or 0.0


