# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	query = """ select  mr.name, mr.transaction_date, mr_item.cost_center_w, mr_item.warehouse, mr_item.item_code, mr_item.item_name, 
	mr_item.item_group, mr_item.material_sub_group, mr_item.description,  sum(ifnull(mr_item.qty, 0)), sum(ifnull(mr_item.ordered_qty, 0)), 
	(sum(mr_item.qty) - sum(ifnull(mr_item.ordered_qty, 0))) 
	from
       	 `tabMaterial Request` mr, `tabMaterial Request Item` mr_item
	where
        mr_item.parent = mr.name
        and mr.material_request_type = "Purchase"
        and mr.docstatus = 1
        and mr.status != "Stopped" """
	if filters.from_date and filters.to_date:
		query += " and mr.transaction_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))

	if filters.item_code:
		query += " and mr_item.item_code = '{0}'".format(filters.get("item_code"))
	if filters.item_group:
		query += " and mr_item.item_group = '{0}'".format(filters.get('item_group'))

	if filters.item_sub_group:
		query += " and mr_item.material_sub_group = '{0}'".format(filters.get('item_sub_group'))
	if filters.cost_center:
		query += " and mr_item.cost_center_w = '{0}'".format(filters.get('cost_center'))
	if filters.warehouse:
		query += " and mr_item.warehouse = '{0}'".format(filters.get('warehouse'))
	
	query += """ group by mr.name, mr_item.item_code having sum(ifnull(mr_item.ordered_qty, 0)) < sum(ifnull(mr_item.qty, 0))
	order by mr.transaction_date desc
		"""

	return frappe.db.sql(query)

def get_columns(filters):
	return [
		{
                  "fieldname": "mr_name",
                  "label": "Material Request",
                  "fieldtype": "Link",
                  "options": "Material Request",
                  "width": 100
                },
		{
                  "fieldname": "pr_date",
                  "label": "PR Date",
                  "fieldtype": "Date",
                  "width": 100
                },
		{
                  "fieldname": "cost_center",
                  "label": "Requesting Cost Center",
                  "fieldtype": "Link",
                  "options": "Cost Center",
                  "width": 100
                },
		{
                  "fieldname": "warehouse",
                  "label": "Requesting Warehouse",
                  "fieldtype": "Link",
                  "options": "Warehouse",
                  "width": 100
                },
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
                  "fieldname": "pr_qty",
                  "label": "PR Qty",
                  "fieldtype": "Float",
                  "width": 100
                },
		{
                  "fieldname": "po_qty",
                  "label": "PO Qty",
                  "fieldtype": "Float",
                  "width": 100
                },
		{
                  "fieldname": "pending",
                  "label": "PO Pending",
                  "fieldtype": "Float",
                  "width": 100
                }
	]
