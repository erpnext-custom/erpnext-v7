# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns(filters)
        data = get_data(filters)
        return columns, data

def get_data(filters):
        data = []

	return data


def get_columns(filters):
	columns = [
                {
                  "fieldname": "sales_order",
                  "label": "Sales Order",
                  "fieldtype": "Link",
                  "options": "Sales Order",
                  "width": 100
                },
                {
                  "fieldname": "posting_date",
                  "label": "SO Date",
                  "fieldtype": "Date",
                  "width": 90
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
                  "width": 125
                },
                {
                  "fieldname": "customer",
                  "label": "Customer Name",
                  "fieldtype": "Link",
                  "options": "Customer",
                  "width": 140
                },
		{
                  "fieldname": "customer_type",
                  "label": "Customer Type",
                  "fieldtype": "Data",
                  "width": 140
                },
                {
                  "fieldname": "customer_id",
                  "label": "Customer ID/Work Permit",
                  "fieldtype": "Data",
                  "width": 150
                },
                {
                  "fieldname": "customer_contact",
                  "label": "Customer Contact",
                  "fieldtype": "Data",
                  "width": 120
                },
                {
                  "fieldname": "qty",
                  "label": "Invoiced Qty",
                  "fieldtype": "Float",
                  "width": 90
                },
                {
                  "fieldname": "rate",
                  "label": "Rate",
                  "fieldtype": "Float",
                  "width": 70
                },
                {
                  "fieldname": "amount",
                  "label": "Amount",
                  "fieldtype": "Currency",
                  "width": 110
                },
		
	]

	return columns

