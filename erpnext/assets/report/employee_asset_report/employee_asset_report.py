# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	columns = get_columns();
	queries = construct_query(filters);
	data = get_data(queries);

	return columns, data

def get_data(query):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		row = [d.employee_id, d.employee_name, d.name, d.asset_name, d.purchase_date, d.gross_purchase_amount]
		data.append(row);

	return data

def construct_query(filters=None):
	query ="""
		SELECT 
			e.name employee_id, e.employee_name,
			a.name, a.asset_name, a.purchase_date, a.gross_purchase_amount, a.status 
		FROM 
			`tabAsset` as a 
			LEFT JOIN
			`tabEmployee` as e ON a.issued_to = e.name 
		WHERE 	a.docstatus = 1 
		and 	a.status in ('Submitted','Partially Depreciated','Fully Depreciated')
		"""
	if filters.employee:
		query += " and a.issued_to = \'" + str(filters.employee) + "\'"
	
	return query;

def get_columns():
	return [
		{
		 "fieldname": "employee_id",
		 "label": "Employee ID",
		 "fieldtype": "Data",
		 "width": 100
		},
		{
		 "fieldname": "employee_name",
		 "label": "Employee Name",
		 "fieldtype": "Data",
		 "width": 150
		},
		{
		  "fieldname": "name",
		  "label": "Asset Code",
		  "fieldtype": "Link",
		  "options": "Asset",
		  "width": 150
		},
		{
		  "fieldname": "asset_name",
		  "label": "Asset Name",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
		  "fieldname": "purchase_date",
		  "label": "Issued On",
		  "fieldtype": "Date",
		  "width": 150
		},
		{
		  "fieldname": "gross_amount",
		  "label": "Price",
		  "fieldtype": "Currency",
		  "width": 150
		},
		#{
		#  "fieldname": "status",
		#  "label": "Asset Status",
		#  "fieldtype": "Data",
		#  "width": 150
		#}
	]
