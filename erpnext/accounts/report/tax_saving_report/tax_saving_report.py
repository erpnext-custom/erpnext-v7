# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

def get_data(filters):
	query = "select pi.supplier_name, pi.bill_no, pii.item_code, pii.item_name, pii.qty, pii.rate, pii.amount, pii.cost_center, pii.warehouse, pii.excise_duty, pii.excise_equalization_tax, pii.sales_tax, pii.green_tax, pii.customs_duty, pii.gst, pii.direct_tax1, pii.direct_tax2, pii.direct_tax3, pii.direct_tax4, pii.excise_duty+pii.excise_equalization_tax+pii.sales_tax+pii.green_tax+pii.green_tax+pii.customs_duty+pii.gst+pii.direct_tax1+pii.direct_tax2+pii.direct_tax3+pii.direct_tax4 as total_tax_exemption from `tabPurchase Invoice` pi, `tabPurchase Invoice Item` pii where pi.name = pii.parent and pi.posting_date >= \'"+str(filters.from_date)+"\' and pi.posting_date <= \'"+str(filters.to_date)+"\'"

	if filters.cost_center:
		query+=" and cost_center = \'"+filters.cost_center+"\'"

	if filters.supplier:
		query+=" and supplier = \'"+filters.supplier+"\'"

	data = frappe.db.sql(query, as_dict=True)
	
	return data


def get_columns():
	return [
			{
				"fieldname": "supplier_name",
				"label": ("Supplier Name"),
				"fieldtype": "Link",
				"options" : "Supplier",
				"width": 120
			},
			{
				"fieldname": "item_code",
				"label": ("Material Code"),
				"fieldtype": "Link",
				"options": "Item",
				"width": 120
			},
			{
				"fieldname": "item_name",
				"label": ("Material Name"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "bill_no",
				"label": ("Invoice Number"),
				"fieldtype": "Data",
				"width": 120
			},
			{
				"fieldname": "qty",
				"label": ("Invoice Qty"),
				"fieldtype": "Data",
				"width": 120
			},
			{
				"fieldname": "rate",
				"label": ("Invoice Rate"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "amount",
				"label": ("Amount"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "cost_center",
				"label": ("Cost Center"),
				"fieldtype": "Link",
				"options":"Cost Center",
				"width": 130
			},
			{
				"fieldname": "warehouse",
				"label": ("Warehouse"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "excise_duty",
				"label": ("Excise Duty"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "excise_equalization_tax",
				"label": ("Excise Equalization Tax"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "sales_tax",
				"label": ("Sales Tax"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "green_tax",
				"label": ("Green Tax"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "customs_duty",
				"label": ("Customs Duty"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "gst",
				"label": ("GST"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "direct_tax1",
				"label": ("Direct Tax - 2%"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "direct_tax2",
				"label": ("Direct Tax - 3%"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "direct_tax3",
				"label": ("Direct Tax - 5%"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "direct_tax4",
				"label": ("Direct Tax - 10%"),
				"fieldtype": "Data",
				"width": 130
			},
			{
				"fieldname": "total_tax_exemption",
				"label": ("Total Tax Exemption"),
				"fieldtype": "Data",
				"width": 130
			},
		]
		
	return columns