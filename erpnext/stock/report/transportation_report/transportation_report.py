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
	query = "select distinct dn.transporter_name1, dn.lr_no, dn.lr_date, dn.customer, dn.name, dn.posting_date, dni.item_code, dni.item_name, sii.delivered_qty, sii.accepted_qty, (ifnull(sii.delivered_qty, 0) - ifnull(sii.accepted_qty,0)) as difference_qty, sii.abnormal_loss, sii.normal_loss, sii.abnormal_loss_amt, sii.normal_loss_amt, case when sii.loss_method = 'Quantity in Flat' then sii.loss_qty_flat else concat(sii.loss_tolerance, '%') end as loss_tolerance, sii.parent as sales_invoice, (select si.posting_date from `tabSales Invoice` as si where si.name = sii.parent) as si_date, (select si.sales_invoice_date from `tabSales Invoice` as si where si.name = sii.parent) as ref_date, sii.loss_method, sii.remarks, sii.justification from `tabDelivery Note` as dn LEFT JOIN `tabDelivery Note Item` as dni on dni.parent = dn.name LEFT JOIN `tabSales Invoice Item` as sii on sii.delivery_note = dn.name where dn.status = \'Completed\' and sii.docstatus = 1 and  dn.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"

	if filters.transporter:
		query+=" and dn.transporter_name1 = \'" + filters.transporter + "\'"

	if filters.customer:
		query+=" and dn.customer = \'" + filters.customer + "\'"

	trans_data = frappe.db.sql(query, as_dict=True)
	
	data = []

	if trans_data:
		for a in trans_data:
			row = {
				"customer_name": a.customer,
				"transporter_name": a.transporter_name1,
				"item_name": a.item_name,
				"vehicle_no": a.lr_no,
				"dispatch_date": a.lr_date,
				"delivery_note": a.name,
				"dn_date": a.posting_date,
				"sales_invoice": a.sales_invoice,
				"si_date": a.si_date,
				"ref_date": a.ref_date,
				"delivered_qty": a.delivered_qty,
				"accepted_qty": a.accepted_qty,
				"difference_qty": a.difference_qty,
				"tolerance": a.loss_tolerance,
				"normal_loss_qty": a.normal_loss,
				"abnormal_loss_qty": a.abnormal_loss,
				"normal_loss_amount": a.normal_loss_amt,
				"abnormal_loss_amount": a.abnormal_loss_amt,
				"normal_loss_text": a.remarks,
				"abnormal_loss_text": a.justification,
				"tolerance_based_on": a.loss_method,
			}
			data.append(row)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "transporter_name",
			"label": _("Transporter Name"),
			"fieldtype": "Link",
			"options":"Supplier",
			"width": 200
		},
		{
			"fieldname": "vehicle_no",
			"label": _("Vehicle No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "dispatch_date",
			"label": _("Vehicle Dispatch Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "ref_date",
			"label": _("Reference Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "customer_name",
			"label": _("Customer Name"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200
		},
		{
			"fieldname": "delivery_note",
			"label": _("Delivery Note"),
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 150
		},
		{
			"fieldname": "dn_date",
			"label": _("DN Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "sales_invoice",
			"label": _("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150
		},
		{
			"fieldname": "si_date",
			"label": _("SI Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "item_name",
			"label": _("Material Name"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "delivered_qty",
			"label": _("Delivered Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "accepted_qty",
			"label": _("Accepted Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "difference_qty",
			"label": _("Difference Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "tolerance",
			"label": _("Tolerance"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "tolerance_based_on",
			"label": _("Tolerance Method"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "normal_loss_qty",
			"label": _("Normal Loss Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "abnormal_loss_qty",
			"label": _("Abnormal Loss Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "normal_loss_amount",
			"label": _("Normal Loss Amount"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "abnormal_loss_amount",
			"label": _("Abnormal Loss Amount"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "normal_loss_text",
			"label": _("Normal Loss Remark"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "abnormal_loss_text",
			"label": _("Abnormal Loss Remark"),
			"fieldtype": "Data",
			"width": 150
		}
	]

