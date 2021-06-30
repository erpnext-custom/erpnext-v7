# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers, get_period_date


def execute(filters=None):
       
	columns = get_columns(filters)
        data = get_data(filters)

        return columns, data

def get_columns(filters):
	if filters.uinput == "Production":
		cols= [
				("Region") + ":Link/Cost Center:140",
				("Branch") + ":Link/Branch:140",
				("Production Group") + ":Data:140",
				("Material Group") + ":Link/Item Group:140",
				("1st Quarter") + ":Float:90",
				("2nd Quarter") + ":Float:90",
				("3rd Quarter") + ":Float:90",
				("4th Quarter") + ":Float:90",
				("Target Qty") + ":Float:90"
        	]
	else:
		cols=[
				("Region") + ":Link/Cost Center:140",
				("Branch") + ":Link/Branch:140",
				("Disposal Group") + ":Data:140",
				("Material Group") + ":Link/Item Group:140",
				("1st Quarter") + ":Float:90",
				("2nd Quarter") + ":Float:90",
				("3rd Quarter") + ":Float:90",
				("4th Quarter") + ":Float:90",
				("Disposal Qty") + ":Data:97"
		]
	return cols 

def get_data(filters):
	all_ccs = get_child_cost_centers(filters.cost_center)

	if not filters.uinput:
		return []
	query = "select (select cc.parent_cost_center from `tabCost Center` cc where cc.name = pt.cost_center) as region, pt.branch, pdi.production_group, pt.item_group, sum(pdi.quarter1), sum(pdi.quarter2), sum(pdi.quarter3), sum(pdi.quarter4), sum(pdi.quantity) from `tab{0} Target Item` pdi, `tabProduction Target` pt where pt.name = pdi.parent".format(filters.uinput) 

	#--------CONDITIONS------------------------------------------------------#
	if filters.branch:
		branch = str(filters.branch)
		branch = branch.replace(' - NRDCL','')
		query += " and pt.branch = '"+branch+"'"

	else:	
		query += " and pt.cost_center in {0} ".format(tuple(all_ccs))
			
	if filters.get("location"):
		query += " and pt.location = \'" + str(filters.location) + "\'"

	if filters.get("fiscal_year"):
		query += " and pt.fiscal_year = \'" + str(filters.fiscal_year) + "\'"

	if filters.get("item_group"):
		query += " and pt.item_group = '{0}'".format(filters.get("item_group"))

	query += " group by pdi.production_group " 
	# if frappe.session.user == "Administrator":
	# 	frappe.throw(query)
	return frappe.db.sql(query)
