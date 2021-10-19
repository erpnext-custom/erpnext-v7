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
	query = "select pi.posting_date as date, pi.supplier, pii.item_code, pii.item_group, (select isg.item_sub_group from `tabItem` isg where isg.name = pii.item_code) as item_sub_group, pii.cost_center, pii.warehouse, pii.item_name, pi.name as purchase_invoice, pi.base_write_off_amount as penalty_amount, pi.write_off_description as remarks from `tabPurchase Invoice` pi, `tabPurchase Invoice Item` pii where pi.name = pii.parent and pi.docstatus = 1 and pi.base_write_off_amount > 0"

	if filters.from_date and filters.to_date:
		query += " and pi.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"

	if filters.item_code:
		query += " and pii.item_code = '{0}'".format(filters.get("item_code"))

	if filters.item_group:
                query += " and pii.item_group = '{0}'".format(filters.get("item_group"))

	if filters.item_sub_group:
                query += " and exists ( select 1 from `tabItem` i where i.item_sub_group = '{0}' and i.name = pii.item_code)".format(filters.get("item_sub_group"))

	if filters.cost_center:
                query += " and pii.cost_center = '{0}'".format(filters.get("cost_center"))

	if filters.warehouse:
                query += " and warehouse = '{0}'".format(filters.get("warehouse"))

	query += " order by pi.posting_date"

	fines_data = frappe.db.sql(query, as_dict=True)
	
	data = []

	if fines_data:
		for a in fines_data:
			row = {
				"date": a.date,
				"supplier": a.supplier,
				"item_code": a.item_code,
				"item_name": a.item_name,
				"item_group": a.item_group,
				"item_sub_group": a.item_sub_group,
				"cost_center": a.cost_center,
				"purchase_invoice": a.purchase_invoice,
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
			"fieldname": "supplier",
			"label": _("Vendor"),
			"fieldtype": "Link",
			"options":"Supplier",
			"width": 200
		},
		{
			"fieldname": "item_code",
			"label": _("Material Code"),
			"fieldtype": "Link",
			"options": "Item",
			"width": 100
		},
		{
			"fieldname": "item_name",
			"label": _("Material Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
                        "fieldname": "item_group",
                        "label": _("Material Group"),
                        "fieldtype": "Link",
                        "options": "Item Group",
                        "width": 120
                },
		{
                        "fieldname": "item_sub_group",
                        "label": _("Material Sub Group"),
                        "fieldtype": "Link",
                        "options": "Item Sub Group",
                        "width": 170
                },
		{
                        "fieldname":"cost_center",
                        "label": _("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
			"width": 160
                },
		{
                        "fieldname":"warehouse",
                        "label": _("Warehouse"),
                        "fieldtype": "Link",
                        "options": "Warehouse",
			"width": 150
                },

		{
			"fieldname": "purchase_invoice",
			"label": _("Purchase Invoice"),
			"fieldtype": "Link",
			"options": "Purchase Invoice",
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

