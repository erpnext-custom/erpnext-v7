# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

def get_data(filters):
	query = "select case when sales_order != 'NULL' then 'Sold' when production != 'NULL' then 'Taken For Sawing' when stock_entry != 'NULL' then 'Stock Transfered' else 'Unsold' end as status , item as item_code, item_name, item_sub_group as type,total_volume as volume,lot_no, monthname(posting_date) as month,branch,warehouse from `tabLot List` where posting_date >= \'"+str(filters.from_date)+"\' and posting_date <= \'"+str(filters.to_date)+"\'"

	if filters.branch:
		query+=" and branch = \'"+filters.branch+"\'"

	if filters.warehouse:
		query+=" and warehouse = \'"+filters.warehouse+"\'"

	if filters.type:
		query+=" and item_sub_group = \'"+filters.type+"\'"

	if filters.item_code:
		query+=" and item = \'"+filters.item_code+"\'"

	data = frappe.db.sql(query, as_dict=True)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options" : "Item",
			"width": 120
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "volume",
			"label": _("Total Volume(cft)"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "lot_no",
			"label": _("Lot Number"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "month",
			"label": _("Month"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "branch",
			"label": _("Branch"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Data",
			"width": 130
		},
	]
	
	return columns
