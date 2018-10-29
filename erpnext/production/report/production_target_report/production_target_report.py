# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

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
			("Sales Group") + ":Data:140",
			("Sales Qty") + ":Data:90"
		]
	return cols

def get_data(filters):
	if not filters.uinput:
		return []
	query = "select pdi.production_group, pdi.quantity from `tab{0} Target Item` pdi, `tabProduction Target` pt where pt.name = pdi.parent".format(filters.uinput) 

	#CHECK BRA|NCH
	#IF BRANCH THEN UNIT ., THEREFORE USE =
	#ELSE, PARENT CC, THEREFORE USE IN
	if filters.get("cost_center"):
		query += " and pt.cost_center = \'" + str(filters.cost_center) + "\'"	
	
	if filters.get("location"):
		query += " and pt.location = \'" + str(filters.location) + "\'"
	if filters.get("fiscal_year"):
		query += " and pt.fiscal_year = \'" + str(filters.fiscal_year) + "\'"	
	query += " group by pdi.production_group " 

	return frappe.db.sql(query)
