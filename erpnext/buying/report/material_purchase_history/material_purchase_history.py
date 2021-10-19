# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_data(filters):
	query = """SELECT po_item.item_code, po_item.item_name, po_item.item_group, (select isg.item_sub_group from `tabItem` isg 
		where isg.name = po_item.item_code) as item_sub_group, po_item.description,  po_item.qty, po_item.uom, po_item.base_rate, 
		po_item.base_amount, po.name, po.transaction_date, po_item.cost_center, po_item.warehouse, po.supplier, sup.supplier_name, 
		sup.supplier_type, 
		CASE WHEN sup.inter_company = 1 THEN 'Yes' ELSE 'No' END as dhi_owned, po_item.project, ifnull(po_item.received_qty, 0)
		FROM
		`tabPurchase Order` po, `tabPurchase Order Item` po_item, `tabSupplier` sup
		WHERE	
		po.name = po_item.parent and po.supplier = sup.name and po.docstatus = 1"""

	if filters.from_date and filters.to_date:
		query += " and po.transaction_date between '{0}' and '{1}'".format(filters.get('from_date'), filters.get('to_date'))
	
	if filters.item_code:
                query += " and po_item.item_code = '{0}'".format(filters.get("item_code"))
        if filters.item_group:
                query += " and po_item.item_group = '{0}'".format(filters.get('item_group'))

        if filters.item_sub_group:
                query += " and exists ( select 1 from `tabItem` where name = po_item.item_code and item_sub_group = '{0}')".format(filters.get('item_sub_group'))
        if filters.cost_center:
                query += " and po_item.cost_center = '{0}'".format(filters.get('cost_center'))
        if filters.warehouse:
                query += " and po_item.warehouse = '{0}'".format(filters.get('warehouse'))

	query += " ORDER BY po.name desc"
	
	return frappe.db.sql(query)

def get_columns(filters):
	return [
		{
                  "fieldname": "item_code",
                  "label": "Material Code",
                  "fieldtype": "Link",
                  "options": "Item",
                  "width": 100
                },
                {
                  "fieldname": "item_name",
                  "label": "Material Name",
                  "fieldtype": "Data",
                  "width": 150
                },
                {
                  "fieldname": "item_group",
                  "label": "Material Group",
                  "fieldtype": "Link",
                  "options": "Item Group",
                  "width": 170
                },

                {
                  "fieldname": "item_sub_group",
                  "label": "Material Sub Group",
                  "fieldtype": "Link",
                  "options": "Item Sub Group",
                  "width": 170
                },
                {
                  "fieldname": "description",
                  "label": "Material Description",
                  "fieldtype": "Data",
                  "width": 170
                },
                
               {
                  "fieldname": "po_qty",
                  "label": "PO Qty",
                  "fieldtype": "Float",
                  "width": 100
                },
                {
                  "fieldname": "uom",
                  "label": "UOM",
                  "fieldtype": "Link",
                  "options": "UOM",
                  "width": 100
                },
                {
                  "fieldname": "base_rate",
                  "label": "Rate",
                  "fieldtype": "Currency",
                  "width": 100
                },
                {
                  "fieldname": "amount",
                  "label": "Amount",
                  "fieldtype": "Currency",
                  "width": 100
                },
               
                {
                  "fieldname": "pr_name",
                  "label": "Purchase Order",
                  "fieldtype": "Link",
                  "options": "Purchase Order",
                  "width": 100
                },
                {
                  "fieldname": "po_date",
                  "label": "PO Date",
                  "fieldtype": "Date",
                  "width": 100
                },
		 {
                  "fieldname": "cost_center",
                  "label": "Cost Center",
                  "fieldtype": "Link",
                  "options": "Cost Center",
                  "width": 100
                },
                {
                  "fieldname": "warehouse",
                  "label": "Warehouse",
                  "fieldtype": "Link",
		  "options": "Warehouse",
                  "width": 100
                },

		{
                  "fieldname": "vendor",
                  "label": "Vendor",
                  "fieldtype": "Link",
                  "options": "Supplier",
                  "width": 100
                },
                {
                  "fieldname": "vendor_name",
                  "label": "Vendor Name",
                  "fieldtype": "Data",
                  "width": 100
                },
                
                {  "fieldname": "vendor_type",
                  "label": "Vendor Type",
                  "fieldtype": "Link",
                  "options": "Supplier Type",
                  "width": 100
                },
                
                {
                  "fieldname": "dhi_owned",
                  "label": "DHI Owned Company",
                  "fieldtype": "Data",
                  "width": 100
                },
		{
                  "fieldname": "project",
                  "label": "Project",
                  "fieldtype": "Link",
                  "options": "Project",
                  "width": 100
                },
		{
                  "fieldname": "received_qty",
                  "label": "Received Qty",
                  "fieldtype": "Float",
                  "width": 100
                }
	]
