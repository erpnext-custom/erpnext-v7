# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	#columns = get_columns(filters)
	data = get_data(filters)
	columns = get_columns(filters)
	return columns, data

def get_columns(filters):
	cols=[
		("Material Name") + ":Data:200",
		("Material Group") + ":Data:120",
	 	("From Date") + ":Data:120",
		("To Date") + ":Data:120",
		("UoM")+":Data:80",
		("Rate(Nu") + ":Data:120",
		("Created By") + ":Data:180",
		("Created On") + ":Data:180"
	]
			
	return cols

def get_data(filters):
	query= """
			select item_name, naming_series,from_date, to_date, uom, rate_amount,owner,creation 
			from `tabStock Price Template` 
			where purpose = '{0}' 
			and docstatus =1
			order by naming_series, item_name, from_date, creation
		""".format(filters.get("uinput"))

	return frappe.db.sql(query)
