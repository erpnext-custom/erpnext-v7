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
	query = "select item as item_code, item_name, item_sub_group as type, lot_no, monthname(posting_date) as month from `tabLot List` where posting_date >= \'"+str(filters.from_date)+"\' and posting_date <= \'"+str(filters.to_date)+"\'"

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
			"fieldname": "lot_no",
			"label": _("Lot Number"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "month",
			"label": _("Month"),
			"fieldtype": "Data",
			"width": 130
		},
	]
	
	return columns
