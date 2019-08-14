# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	cols = [
		("Date") + ":date:100",
		("Material Code") + ":data:110",
		("Material Name")+":data:120",
		("Material Group")+":data:120",
		("UoM") + ":data:50",
		("Qty")+":data:50",
		("Valuation Rate")+":data:120",
		("Amount")+":Currency:110",
	]
	if filters.purpose == "Material Issue":
		cols.append(("Cost Center")+":data:170")
		cols.append(("Issued To")+":data:120")

	if filters.purpose == "Material Transfer":
		cols.insert(6,{ "fieldname": "received_qty", "label": "Received Qty", "fieldtype": "Data","width": 100}),
		cols.insert(7,{ "fieldname": "difference_qty", "label": "Difference Qty", "fieldtype": "Data","width": 100}),
		cols.append(("Source Warehouse")+":data:170")
		cols.append(("Destination Warehouse")+":data:170")
		cols.append(("Equipment Model")+":data:140")
		cols.append(("Equipment Number")+":data:170")
	cols.append(("Stock Entry")+":Link/Stock Entry:170")
	return cols

def get_data(filters):
	if filters.purpose == 'Material Transfer':
		data = "select se.posting_date, sed.item_code, sed.item_name, (select i.item_group from tabItem i where i.item_code = sed.item_code) as item_group, sed.uom, sed.qty, sed.received_qty, sed.difference_qty, sed.valuation_rate, sed.received_qty*sed.valuation_rate, sed.s_warehouse, sed.t_warehouse, se.equipment_model, se.equipment_number, se.name FROM `tabStock Entry` se, `tabStock Entry Detail` sed WHERE se.name = sed.parent and  se.docstatus = 1 and se.purpose = 'Material Transfer'"
	elif filters.purpose == 'Material Issue':
		data = "select se.posting_date, sed.item_code, sed.item_name, (select i.item_group from tabItem i where i.item_code = sed.item_code) as item_group, sed.uom, sed.qty, sed.valuation_rate,sed.amount, sed.cost_center, sed.issued_to, se.name FROM `tabStock Entry` se, `tabStock Entry Detail` sed WHERE se.name = sed.parent and  se.docstatus = 1 and se.purpose = 'Material Issue'"
	if filters.get("warehouse"):
		data += " and sed.s_warehouse = \'" + str(filters.warehouse) + "\'"
	if filters.get("item_code"):
		data += " and sed.item_code = \'" + str(filters.item_code) + "\'"
	if filters.get("from_date") and filters.get("to_date"):
		data += " and se.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	if filters.get("equipment_type"):
                data += " and se.equipment_type = '{0}'".format(filters.get("equipment_type"))	
	return frappe.db.sql(data)
