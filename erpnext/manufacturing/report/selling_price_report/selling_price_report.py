# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

#########Created by Cheten Tshering on 17/09/2020 ##################################
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(filters),get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		_("Product Code") + ":Link/Item:150",
		_("Product Name") + ":Data:150",
		_("BOM") + ":Link/BOM:150",
		_("BOM Cost") + ":Currency:150",
		_("Prime Cost") + ":Currency:150",
		_("Manufacturing Cost") + ":Currency:150",
		_("Cost of Production") + ":Currency:150",
		_("Selling Price") + ":Currency:150",
		_("Cost Sheet") + "::150"

	]
	return columns

def get_data(filters):
	cond = get_conditions(filters)
	data = frappe.db.sql("""
		select 
			cs.item, 
			cs.item_name, 
			cs.bom, 
			cs.bom_cost, 
			cs.prime_cost, 
			cs.manufacturing_cost, 
			cs.production_cost, 
			cs.selling_price, 
			cs.name
		from `tabCost Sheet` cs
		where cs.docstatus = 1 
		and '{date}' >= cs.from_date
		{condition}
	""".format(date=filters.date, condition=cond))
	return data

def get_conditions(filters):
	cond = ""
	if filters.branch:
		cond += """ and branch = "{}" """.format(filters.branch)
	if filters.item:
		cond += """and item = "{}" """.format(filters.item)
	return cond