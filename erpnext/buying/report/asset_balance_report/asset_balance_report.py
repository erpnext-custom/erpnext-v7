# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	columns = get_columns();
	queries = construct_query(filters);
	data = get_data(queries, filters);

	return columns, data

def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		if not d.issued_qty:
			d.issued_qty = 0

		row = [d.item_code, d.item_name, d.item_group, d.item_sub_group, d.cost_center, d.total_qty, d.issued_qty, flt(d.total_qty) - flt(d.issued_qty)]
		data.append(row);
	return data

def construct_query(filters=None):
	query = """
		select 
			ae.item_code, 
			(select i.item_name from `tabItem` as i where i.item_code = ae.item_code) as item_name, 
			(select ig.item_group from `tabItem` ig where ig.name = ae.item_code) as item_group, 
			(select isg.item_sub_group from `tabItem` isg where isg.name = ae.item_code) as item_sub_group,
			sum(ae.qty) as total_qty, 
			(select sum(id.qty) from `tabAsset Issue Details` id where id.item_code = ae.item_code and id.docstatus = 1) as issued_qty 
		from `tabAsset Received Entries` as ae 
		where ae.docstatus = 1 and exists(select 1 from `tabItem` where item_code = ae.item_code)
	"""

	if filters.to_date and filters.from_date:
		query = "select ae.item_code, (select i.item_name from `tabItem` as i where i.item_code = ae.item_code) as item_name, ae.qty as total_qty, (select sum(id.qty) from `tabAsset Issue Details` id where id.item_code = ae.item_code and id.docstatus = 1 and id.issued_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\') as issued_qty from `tabAsset Received Entries` as ae where ae.docstatus = 1 and exists(select 1 from `tabItem` where item_code = ae.item_code) and ae.received_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"; 
	
	query += " group by ae.item_code order by ae.item_code asc"
	return query;


def get_columns():
	return [
		{
		  "fieldname": "item_code",
		  "label": "Material Code",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "item_name",
		  "label": "Material Name",
		  "fieldtype": "Data",
		  "width": 250
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
                  "fieldname": "cost_center",
                  "label": "Cost Center",
                  "fieldtype": "Link",
                  "options": "Cost Center",
                  "width": 170
                },
		{
		  "fieldname": "total_qty",
		  "label": "Total Quantity",
		  "fieldtype": "Data",
		  "width": 120
		},
		{
		  "fieldname": "issued_qty",
		  "label": "Issued Quantity",
		  "fieldtype": "Data",
		  "width": 120
		},
		{
		  "fieldname": "balance_qty",
		  "label": "Balance Quantity",
		  "fieldtype": "Data",
		  "width": 120
		}
	]
