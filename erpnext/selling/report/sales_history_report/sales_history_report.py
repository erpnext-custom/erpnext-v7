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
	query = "select t1.name as sales_no, t1.transaction_date as sales_date, t1.customer, t1.po_no, t1.po_date, t1.base_net_amount, t1.rate, t1.qty, t1.item_name, t1.item_code, t1.stock_uom, t1.warehouse, t1.delivery_note, t1.delivery_date,t2.invoice_no, t2.ref_date, t2.posting_date, t2.due_date, t2.write_off_amount, t2.write_off_description, t2.total_advance, t1.transporter_name, t2.delivered_qty, t2.accepted_qty, t2.amount, t2.normal_loss_amt, t2.remarks, t2.abnormal_loss_amt, t2.justification, t2.excess_amt, t2.excess_qty from (select so.name, so.transaction_date, so.customer, so.po_no, so.po_date, soi.base_net_amount, soi.rate, soi.qty, soi.item_name, soi.item_code, soi.stock_uom, soi.warehouse, dni.parent as delivery_note, (select transporter_name1 from `tabDelivery Note` as dn where dn.name = dni.parent) as transporter_name, (select posting_date from `tabDelivery Note` as dn where dn.name = dni.parent) as delivery_date from (`tabSales Order` as so JOIN `tabSales Order Item` as soi on so.name = soi.parent and so.docstatus = 1) LEFT JOIN `tabDelivery Note Item` as dni on so.name = dni.against_sales_order and dni.docstatus = 1) as t1 left join (select si.name as invoice_no, si.sales_invoice_date as ref_date, si.posting_date, si.due_date, si.write_off_amount, si.write_off_description, si.total_advance, sii.accepted_qty, sii.delivered_qty, sii.amount, sii.normal_loss_amt, sii.remarks, sii.abnormal_loss_amt, sii.justification, sii.excess_amt, sii.excess_qty, sii.delivery_note as delivery_note_no from `tabSales Invoice` as si, `tabSales Invoice Item` as sii where si.name = sii.parent and si.docstatus = 1) as t2 on t1.delivery_note = t2.delivery_note_no"

	if filters.from_date and filters.to_date:
		query+=" where t2.posting_date BETWEEN  \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"

	if filters.customer:
		query+=" and customer = \'" + filters.customer + "\'"
	
	query += " order by sales_date asc"
	
	sales_data = frappe.db.sql(query, as_dict=True)
	
	data = []
	total = total_billed = nor_amt = ab_amt = ex_amt = ad_amt = to_bill = normal_total  = abnormal_total = 0

	if sales_data:
		for a in sales_data:
			normal_qty = 0;
			abnormal_qty = 0;
			to_bill = flt(a.amount) + flt(a.excess_amt) - flt(a.normal_loss_amt) - flt(a.abnormal_loss_amt)
			if flt(a.normal_loss_amt > 0):
				normal_qty = flt(a.delivered_qty) - flt(a.accepted_qty)
				normal_total += flt(normal_qty)
			
			if flt(a.abnormal_loss_amt > 0):
				abnormal_qty = flt(a.delivered_qty) - flt(a.accepted_qty)
				abnormal_total += flt(abnormal_qty)

			row = {
				"transporter_name": a.transporter_name,
				"sales_no": a.sales_no,
				"sales_date": a.sales_date,
				"customer": a.customer,
				"po_no": a.po_no,
				"po_date": a.po_date,
				"base_net_amount": a.base_net_amount,
				"rate": a.rate,
				"qty": a.qty,
				"item_name": a.item_name,
				"item_code": a.item_code,
				"stock_uom": a.stock_uom,
				"warehouse": a.warehouse,
				"invoice_no": a.invoice_no,
				"sales_invoice_date": a.posting_date,
				"ref_date": a.ref_date,
				"due_date": a.due_date,
				"write_off_amount": a.write_off_amount,
				"write_off_description": a.write_off_description,
				"total_advance": a.total_advance,
				"delivery_note": a.delivery_note,
				"delivery_date": a.delivery_date,
				"delivered_qty": a.delivered_qty,
				"accepted_qty": a.accepted_qty,
				"amount": a.amount,
				"normal_loss_amt": a.normal_loss_amt,
				"remarks": a.remarks,
				"abnormal_loss_amt": a.abnormal_loss_amt,
				"excess_amt": a.excess_amt,
				"excess_qty": a.excess_qty,
				"normal_qty": flt(normal_qty, 2),
				"abnormal_qty": flt(abnormal_qty, 2),
				"total_bill_amt": to_bill,
				"justification": a.justification
			}
			data.append(row)
			total = flt(total) + flt(to_bill) 
			total_billed = total_billed + flt(a.amount)
			nor_amt+=flt(a.normal_loss_amt)
			ab_amt+=flt(a.abnormal_loss_amt)
			ex_amt+=flt(a.excess_amt)
			ad_amt+=flt(a.total_advance)
	
		row = {"normal_qty": flt(normal_total), "abnormal_qty": flt(abnormal_total), "sales_no": "Total", "total_bill_amt":  total, "total_advance": ad_amt, "amount": total_billed, "normal_loss_amt": nor_amt, "abnormal_loss_amt": ab_amt, "excess_amt": ex_amt}
		data.append(row)
	return data

def get_columns():
	return [
		{
			"fieldname": "sales_no",
			"label": _("Sales Order"),
			"fieldtype": "Link",
			"options":"Sales Order",
			"width": 150
		},
		{
			"fieldname": "sales_date",
			"label": _("SO Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "customer",
			"label": _("Customer"),
			"fieldtype": "Link",
			"options":"Customer",
			"width": 200
		},
		{
			"fieldname": "po_no",
			"label": _("Customer PO No"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "po_date",
			"label": _("Customer PO Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "qty",
			"label": _("SO Qty"),
			"fieldtype": "Data",
			"width": 80
		},
		{
			"fieldname": "rate",
			"label": _("Sales Price"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "base_net_amount",
			"label": _("Sales Order Amount"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "item_code",
			"label": _("Material Code"),
			"fieldtype": "Data",
			"width": 90
		},
		{
			"fieldname": "item_name",
			"label": _("Material Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "stock_uom",
			"label": _("UoM"),
			"fieldtype": "Data",
			"width": 70
		},
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "delivery_note",
			"label": _("Delivery No"),
			"fieldtype": "Link",
			"options": "Delivery Note",
			"width": 150
		},
		{
			"fieldname": "delivery_date",
			"label": _("Delivery Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "delivered_qty",
			"label": _("Delivered Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "invoice_no",
			"label": _("Invoice No"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 150
		},
		{
			"fieldname": "sales_invoice_date",
			"label": _("Invoice Date"),
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
			"fieldname": "due_date",
			"label": _("Pay Due Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "accepted_qty",
			"label": _("Accepted Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "amount",
			"label": _("Billed Amount"),
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"fieldname": "normal_qty",
			"label": _("NL Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "normal_loss_amt",
			"label": _("Normal Loss Amount"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "remarks",
			"label": _("Normal Loss Remark"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "abnormal_qty",
			"label": _("ANL Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "abnormal_loss_amt",
			"label": _("Abnormal Loss Amount"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "justification",
			"label": _("Abnormal Loss Remark"),
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "excess_qty",
			"label": _("Excess Qty"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "excess_amt",
			"label": _("Excess Amount"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "total_bill_amt",
			"label": _("Total Bill Amount"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "transporter_name",
			"label": _("Transporter Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "total_advance",
			"label": _("Total Advance"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "write_off_amount",
			"label": _("Penalties"),
			"fieldtype": "Currency",
			"width": 130
		},
		{
			"fieldname": "write_off_description",
			"label": _("Penalty Remarks"),
			"fieldtype": "Data",
			"width": 150
		}
	]

