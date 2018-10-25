# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate
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

def get_target_value(cost_center, production_group, fiscal_year, from_date, to_date, is_location=None):
	if not cost_center or not production_group or not fiscal_year:
		frappe.throw("Value Missing")

	if is_location:
		cond = " a.location = '{0}'".format(cost_center)
	else:
		all_ccs = get_child_cost_centers(cost_center)
		cond = " a.cost_center in {0}".format(tuple(all_ccs))

	query = "select sum(quantity) as total, sum(quarter1) as q1, sum(quarter2) as q2, sum(quarter3) as q3, sum(quarter4) as q4 from `tabProduction Target` a, `tabProduction Target Item` b where a.name = b.parent and {0} and a.fiscal_year = '{1}' and b.production_group = '{2}'".format(cond, fiscal_year, production_group)

	qty = frappe.db.sql(query, as_dict=True)

	q1 = qty and qty[0].q1 or 0
	q2 = qty and qty[0].q2 or 0
	q3 = qty and qty[0].q3 or 0
	q4 = qty and qty[0].q4 or 0
	
	return get_propotional_target(from_date, to_date, q1, q2, q3, q4)

def get_propotional_target(from_date, to_date, q1, q2, q3, q4):
	#Determine the target
	from_month = getdate(from_date).month
	try:
		to_month = getdate(to_date).month
	except:
		to_date = to_date.replace("29", "28")
		to_month = getdate(to_date).month

	if from_month == to_month:
		if from_month in (1,2,3):
			target = q1 / 3
		elif from_month in (4, 5, 6):
			target = q2 / 3
		elif from_month in (7, 8, 9):
			target = q3 / 3
		elif from_month in (10, 11, 12):
			target = q4 / 3
		else:
			frappe.throw("INVALID DATA RECEIVED")
	else:
		if from_month == 1 and to_month == 12:
			target = q1 + q2 + q3 + q4
		elif from_month == 1 and to_month == 3:
			target = q1
		elif from_month == 4 and to_month == 6:
			target = q2
		elif from_month == 7 and to_month == 9:
			target = q3
		elif from_month == 10 and to_month == 12:
			target = q4
		elif from_month == 1 and to_month == 6:
			target = q1 + q2
		elif from_month == 7 and to_month == 12:
			target = q3 + q4
		elif from_month == 1 and to_month == 9:
			target = q1 + q2 + q3
		elif from_month == 1 and to_month == 2:	
			target = (q1 / 3) * 2
		elif from_month == 1 and to_month == 4:	
			target = q1 + q2 / 3
		elif from_month == 1 and to_month == 5:	
			target = q1 + (q2 / 3) * 2
		elif from_month == 1 and to_month == 7:	
			target = q1 + q2 + q3 / 3
		elif from_month == 1 and to_month == 8:	
			target = q1 + q2 + (q3 / 3) * 2
		elif from_month == 1 and to_month == 10:	
			target = q1 + q2 + q3 + q4 / 3
		elif from_month == 1 and to_month == 11:	
			target = q1 + q2 + q3 + (q4 / 3) * 2
		else:
			frappe.throw("INVALID DATA RECEIVED")
	return target




