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
	if filters.uinput == "Production":
		query = """select pti.production_group, pti.quantity from `tabProduction Target Item` pti, `tabProduction Target` pt where pt.name= pti.parent"""
	if filters.uinput == "Sales":
		query = """select pdi.production_group, pdi.quantity from `tabDisposal Target Item` pdi, `tabProduction Target` pt where pt.name = pdi.parent""" 
	if filters.get("cost_center"):
		query += " and pt.cost_center = \'" + str(filters.cost_center) + "\'"	
	
	if filters.get("location"):
		query += " and pt.location = \'" + str(filters.location) + "\'"
	

	return frappe.db.sql(query)
