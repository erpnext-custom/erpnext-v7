# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)

        return columns, data

def get_columns():
        return [
                ("Branch ") + ":Link/Branch:150",
                ("Cost Center") + ":Data:150",
		("Location") + ":Data:150",
                ("Item Sub Group") + ":Data:140",
                ("UoM") + ":Data:70",
                ("Target Qty") + ":Data:90",
		("Produced Qty") + ":Data:90",
		("% Achived") +":Data:90",
                ("Fiscal Year") + ":Data:100"
        ]

def get_data(filters):
	query = """select pt.branch, pt.cost_center, pt.location, pti.item_sub_group, pti.uom, pti.quantity, sum(pe.qty) as qty,(( qty/pti.quantity)/100), pt.fiscal_year from `tabProduction Target` pt, `tabProduction Target Item` pti, `tabProduction Entry` pe where pti.parent=pt.name and pt.location =pe.location and pt.cost_center=pe.cost_center and pe.item_sub_group=pti.item_sub_group"""

	if filters.get("branch"):
		query += " and pt.cost_center = \'" + str(filters.branch) + "\'"	
	if filters.get("branch"):
		query += " and pt.location = \'" + str(filters.location) + "\'"
	if filters.get("branch"):
		query += " and pti.item_sub_group = \'" + str(filters.item_sub_group) + "\'"
	return frappe.db.sql(query)
