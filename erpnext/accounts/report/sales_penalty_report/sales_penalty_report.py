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
	query = "select si.posting_date as date, (select transporter_name1 from `tabDelivery Note` as dn where dn.name = sii.delivery_note) as transporter, si.customer, sii.item_code, sii.item_name, (select parent from `tabMines Quality Record Details` as mr where mr.sales_invoice = si.name) as mr_name, si.name as sales_invoice, si.base_write_off_amount as penalty_amount, si.write_off_description as remarks from `tabSales Invoice` si, `tabSales Invoice Item` sii where si.name = sii.parent and si.docstatus = 1 and si.base_write_off_amount  > 0"
	
	if filters.from_date and filters.to_date:
		query += " and si.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"

	query += " order by si.posting_date"

	fines_data = frappe.db.sql(query, as_dict=True)
	
	data = []

	if fines_data:
		for a in fines_data:
			row = {
				"date": a.date,
				"transporter": a.transporter,
				"customer": a.customer,
				"item_code": a.item_code,
				"item_name": a.item_name,
				"mr_name": a.mr_name,
				"sales_invoice": a.sales_invoice,
				"penalty_amount": a.penalty_amount,
				"remarks": a.remarks
			}
			data.append(row)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "transporter",
			"label": _("Transporter"),
			"fieldtype": "Link",
			"options":"Supplier",
			"width": 200
		},
		{
			"fieldname": "customer",
			"label": _("Customer Name"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200
		},
		{
			"fieldname": "item_code",
			"label": _("Material Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 90
		},
		{
			"fieldname": "mr_name",
			"label": _("Mines Quality Record"),
			"fieldtype": "Link",
			"options": "Mines Quality Record",
			"width": 150
		},
		{
			"fieldname": "sales_invoice",
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150
		},
		{
			"fieldname": "penalty_amount",
			"label": _("Penalty Amount"),
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "remarks",
			"label": _("Remarks"),
			"fieldtype": "Data",
			"width": 150
		}
	]

