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
		query = "select sum(id.qty) as issued_qty from `tabAsset Issue Details` id where id.item_code = %s and id.docstatus = 1"
		if filters.to_date and filters.from_date:
			query += " and id.issued_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"	
		if filters.branch:
			query += " and branch = \'"+str(filters.branch)+"\'"
		i_qty = frappe.db.sql(query, d.item_code, as_dict=True)[0]
		if i_qty:
			issued_qty = i_qty.issued_qty
		else:
			issued_qty = 0

		row = [d.item_code, d.item_name, d.total_qty, issued_qty, flt(d.total_qty) - flt(issued_qty)]
		data.append(row);
	return data

def construct_query(filters=None):
	query = "select ae.item_code, ae.item_name, sum(ae.qty) as total_qty from `tabAsset Received Entries` as ae where ae.docstatus = 1"
	if filters.to_date and filters.from_date:
		query += " and ae.received_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"; 
	if filters.branch:
		query += " and ae.branch = \'"+str(filters.branch)+"\'"
	
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
