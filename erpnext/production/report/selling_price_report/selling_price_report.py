# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	conditions = get_conditions(filters)
	if not filters.get("aggregate"):
		query = frappe.db.sql("""
			SELECT sp.name selling_price_id, sp.from_date, sp.to_date,
				(SELECT group_concat(branch separator ',') 
					FROM `tabSelling Price Branch` spb
					WHERE spb.parent = sp.name) branches,
				CONCAT(spr.location,' ','(',l.branch,')') location,
				spr.price_based_on,  
				spr.particular, spr.item_name, i.stock_uom, spr.timber_type, spr.selling_price,
				i.item_group, i.item_sub_group, i.species,
				sp.owner created_by, sp.creation created_on, sp.modified_by, sp.modified
				FROM `tabSelling Price` sp, `tabSelling Price Rate` spr
				LEFT JOIN `tabItem` i ON i.name = spr.particular
				LEFT JOIN `tabLocation` l ON l.name = spr.location
				WHERE DATE('{}') BETWEEN DATE(sp.from_date) AND DATE(sp.to_date)
				AND spr.parent = sp.name
				ORDER BY from_date, to_date, selling_price_id, spr.price_based_on, spr.particular, spr.timber_type;
		""".format(filters.get("report_date")))
	else:
		query = frappe.db.sql("""
			SELECT sp.name selling_price_id, sp.from_date, sp.to_date,
				spb.branch,
				spr.location, 
				spr.item_name, i.item_group, i.item_sub_group, ts.timber_class, spr.selling_price
				FROM `tabSelling Price` sp, `tabSelling Price Branch` spb, `tabSelling Price Rate` spr
				LEFT JOIN `tabItem` i ON i.name = spr.particular
				LEFT JOIN `tabLocation` l ON l.name = spr.location
				LEFT JOIN `tabTimber Species` ts ON ts.name = i.species
				WHERE DATE('{}') BETWEEN DATE(sp.from_date) AND DATE(sp.to_date)
				AND spr.parent = sp.name
				AND spb.parent = sp.name
				AND l.branch = spb.branch
				ORDER BY from_date, to_date, selling_price_id, spr.price_based_on, spr.particular, spr.timber_type;
		""".format(filters.get("report_date")))

	return query

def get_conditions(filters):
	cond = ""
	if filters.get("branch"):
		if not filters.get("aggregate"):
			frappe.throw("Please tick Show Aggregate")
		else:
			cond += " and spb.branch = '{0}'".format(filters.get("branch"))

	if filters.get("location"):
		if not filters.get("aggregate"):
			frappe.throw("Please tick Show Aggregate")
		else:
			cond += " and spr.location = '{0}'".format(filters.get("location"))

	if filters.get("from_date"):
		if not filters.get("aggregate"):
			frappe.throw("Please tick Show Aggregate")
		else:
			cond += " and DATE(sp.from_date) >= DATE('{0}')".format(filters.get("from_date"))

	if filters.get("to_date"):
		if not filters.get("aggregate"):
			frappe.throw("Please tick Show Aggregate")
		else:
			cond += " and DATE(sp.to_date) <= DATE('{0}')".format(filters.get("to_date"))

	if filters.get("item_code"):
		cond += """ and spr.particular = '{0}' """.format(filters.get("item_code"))

	if filters.get("item_group"):
		cond += """ and i.item_group = '{0}' """.format(filters.get("item_group"))

	if filters.get("item_sub_group"):
		cond += """ and i.item_sub_group = '{0}' """.format(filters.get("item_sub_group"))

	if filters.get("timber_class"):
		if not filters.get("aggregate"):
			frappe.throw("Please tick Show Aggregate")
		else:
			cond += """ and ts.timber_class <= '{0}' """.format(filters.get("timber_class"))

def get_columns(filters):
	if filters.get("aggregate"):
		columns = [
				("ID") + ":Link/Selling Price:80",
				("From Date") + ":Date:80",
				("To Date") + ":Date:80",
				("Branch") + "::200",
				("Location") + "::100",
				("Item Name") + "::120",
				("Item Group") + ":Link/Item Group:120",
				("Item Sub Group") + ":Link/Item Sub Group:120",
				("Timber Class") + "::120",
				("Selling Price") + ":Currency:100",
		]
	else:
		columns = [
				("ID") + ":Link/Selling Price:80",
				("From Date") + ":Date:80",
				("To Date") + ":Date:80",
				("Branches") + "::200",
				("Location") + "::100",
				("Price Based On") + "::100",
				("Particular") + "::100",
				("Item Name") + "::120",
				("UOM") + ":Link/UOM:80",
				("Timber Type") + "::120",
				("Selling Price") + ":Currency:100",
				("Item Group") + ":Link/Item Group:120",
				("Item Sub Group") + ":Link/Item Sub Group:120",
				("Species") + "::120",
				("Created By") + "::200",
				("Created On") + "::200",
				("Last Updated By") + "::200",
				("Last Updated On") + "::200"
		]
	return columns
