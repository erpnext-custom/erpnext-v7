# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)

        return columns, data

def get_columns():
        return [
                ("Item Code ") + ":Link/Item:120",
                ("Item name") + ":Data:120",
                ("Planned Qty") + "::80",
                ("On-Order Qty") + ":Data:80",
                ("In Progress") + ":Data:100",
                ("Completed") + ":Data:100",
		("Balance") + ":Data:100"
        ]

def get_data(filters):
	query= """select item_code, item_name, planned_qty, ordered_qty, produced_qty, pending_qty from `tabProduction Plan Item` where docstatus = 1"""
	if filters.get("from_date") and filters.get("to_date"):
                query += " and planned_start_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
	
	return frappe.db.sql(query)
