# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):

	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))


def get_data(filters):
	query = "select name, item_name, customer, transporter_name from `tabMines Quality Record` as mqr where mqr.from_date >= \'" + str(filters.from_date) + "\' and mqr.to_date <= \'" + str(filters.to_date) + "\'"

	if filters.transporter:
		query+=" and mqr.transporter_name = \'" + filters.transporter + "\'"

	if filters.customer:
		query+=" and mqr.customer = \'" + filters.customer + "\'"

	mqr_data = frappe.db.sql(query, as_dict=True)

	data = []

	if mqr_data:
		for a in mqr_data:
			query = "select parent, sample_collected_on, vehicle_no, penalty_amount, remarks, concat(ash_content,' ', ash_uom) as ash_content , concat(moisture_content,' ', moisture_uom) as moisture_content , concat(sulphur_content,' ', sulphur_uom) as sulphur_content from `tabMines Quality Record Details` as mqrd where mqrd.parent = \'" + a.name + "\'"
			mqrd_data = frappe.db.sql(query, as_dict=True)

			if mqrd_data:
				for b in mqrd_data:
					row = {
						"customer_name": a.customer,
						"transporter_name": a.transporter_name,
						"item_name": a.item_name,
						"vehicle_no": b.vehicle_no,
						"fines": b.penalty_amount,
						"inspection_date": b.sample_collected_on,
						"ash_content": b.ash_content,
						"moisture_content": b.moisture_content,
						"sulphur_content": b.sulphur_content,
						"remark": b.remarks,
					}
					data.append(row)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200
		},
		{
			"fieldname": "transporter_name",
			"label": _("Transporter Name"),
			"fieldtype": "Link",
			"options":"Supplier",
			"width": 200
		},
		{
			"fieldname": "item_name",
			"label": _("Material Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "inspection_date",
			"label": _("Inspected On"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "vehicle_no",
			"label": _("Vehicle No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "ash_content",
			"label": _("Ash"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "moisture_content",
			"label": _("Moisture"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "sulphur_content",
			"label": _("Sulphur"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "fines",
			"label": _("Penalties/Fines"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "remark",
			"label": _("Remark"),
			"fieldtype": "Data",
			"width": 200
		},
	]

