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
		("Material Sub Group")+":data:150",
		("UoM") + ":data:50",
		("Qty")+":data:50",
		("Valuation Rate")+":data:120",
		("Amount")+":Currency:110",
	]
	if filters.purpose == "Material Issue":
		cols.append(("Cost Center")+":data:170")
		cols.append(("Site Name")+":data:170")


	if filters.purpose == "Material Transfer":
		cols.append(("Warehouse")+":data:170")
	cols.append(("Stock Entry")+":Link/Stock Entry:170")
	return cols

def get_data(filters):
	if filters.purpose == 'Material Transfer':
		data = "select se.posting_date, sed.item_code, sed.item_name, (select i.item_group from tabItem i where i.item_code = sed.item_code) as item_group, (select i.item_sub_group from tabItem i where i.item_code = sed.item_code) as item_sub_group, sed.uom, sed.qty, sed.valuation_rate,sed.amount, sed.t_warehouse, se.name FROM `tabStock Entry` se, `tabStock Entry Detail` sed WHERE se.name = sed.parent and  se.docstatus = 1 and se.purpose = 'Material Transfer'"
	elif filters.purpose == 'Material Issue':
		data = "select se.posting_date, sed.item_code, sed.item_name, (select i.item_group from tabItem i where i.item_code = sed.item_code) as item_group, (select i.item_sub_group from tabItem i where i.item_code = sed.item_code) as item_sub_group, sed.uom, sed.qty, sed.valuation_rate,sed.amount, sed.cost_center, se.site_name, se.name FROM `tabStock Entry` se, `tabStock Entry Detail` sed WHERE se.name = sed.parent and  se.docstatus = 1 and se.purpose = 'Material Issue'"
	if filters.get("warehouse"):
		data += " and sed.s_warehouse = \'" + str(filters.warehouse) + "\'"
	if filters.get("item_code"):
		data += " and sed.item_code = \'" + str(filters.item_code) + "\'"
	if filters.get("from_date") and filters.get("to_date"):
		data += " and se.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	return frappe.db.sql(data)
