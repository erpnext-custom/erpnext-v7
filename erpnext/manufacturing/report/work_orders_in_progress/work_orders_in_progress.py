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
                ("Date ") + ":Date:120",
                ("Work Order.") + ":Link/Work Order:120",
                ("Item Code") + ":Link/Item:100",
                ("Item Name") + ":Data:170",
                ("Total") + ":Data:120",
                ("In Progress") + ":Data:120",
		("Completed") + ":Data:90",
		("Balance") + ":Data:90"
        ]

def get_data(filters):
	query = """select creation, name,  production_item, item_name, qty, (qty-produced_qty) as progress, produced_qty, "balance" from `tabWork Order` where docstatus =1 and status != 'Stopped' """
	if filters.get("from_date") and filters.get("to_date"):
		query += " and creation between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	return frappe.db.sql(query)
