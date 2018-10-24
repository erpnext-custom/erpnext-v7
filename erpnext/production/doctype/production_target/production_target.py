# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.accounts.utils import get_child_cost_centers

class ProductionTarget(Document):
	def validate(self):
		self.calculate_value()

	def on_update(self):
		self.check_duplicate()

	def check_duplicate(self):
		dups = frappe.db.sql("select name from `tabProduction Target` where branch = %s and location = %s and fiscal_year = %s and name != %s", (self.branch, self.location, self.fiscal_year, self.name), as_dict=True)
		for a in dups:
			frappe.throw("Update {0} to set your targets".format(frappe.get_desk_link("Production Target", a.name)))

		dups = frappe.db.sql("select production_group, count(1) as num from `tabProduction Target Item` where parent = %s group by production_group having num > 1", self.name, as_dict=True)
		for a in dups:
			frappe.throw("Can set only one target for {0}".format(a.production_group))

	def calculate_value(self):
		for a in self.items:
			a.quantity = flt(a.quarter1) + flt(a.quarter2) + flt(a.quarter3) + flt(a.quarter4)

def get_target_value(cost_center, production_group, fiscal_year, is_location=None):
	if not cost_center or not production_group or not fiscal_year:
		frappe.throw("Value Missing")

	if is_location:
		cond = " a.location = '{0}'".format(cost_center)
	else:
		all_ccs = get_child_cost_centers(cost_center)
		cond = " a.cost_center in {0}".format(tuple(all_ccs))

	query = "select sum(quantity) as total from `tabProduction Target` a, `tabProduction Target Item` b where a.name = b.parent and {0} and a.fiscal_year = '{1}' and b.production_group = '{2}'".format(cond, fiscal_year, production_group)

	qty = frappe.db.sql(query, as_dict=True)
	qty = qty and qty[0].total or 0
	return qty



