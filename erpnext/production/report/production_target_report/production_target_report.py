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
             		("Production Group") + ":Data:140",
                	("Target Qty") + ":Data:90"
        	]
	else:
		cols=[
			("Disposal Group") + ":Data:140",
			("Disposal Qty") + ":Data:97"
		]
	return cols 

def get_data(filters):
	all_ccs = get_child_cost_centers(filters.cost_center)

	if not filters.uinput:
		return []
	query = "select pdi.production_group, sum(pdi.quantity) from `tab{0} Target Item` pdi, `tabProduction Target` pt where pt.name = pdi.parent".format(filters.uinput) 

	if filters.get("branch"):
		query += " and pt.cost_center = \'" + str(filters.cost_center) + "\'"	
	else:	
		query += " and pt.cost_center in {0} ".format(tuple(all_ccs))
			
	if filters.get("location"):
		query += " and pt.location = \'" + str(filters.location) + "\'"
	if filters.get("fiscal_year"):
		query += " and pt.fiscal_year = \'" + str(filters.fiscal_year) + "\'"	
	query += " group by pdi.production_group " 

	return frappe.db.sql(query)
