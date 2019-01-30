# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)

        return columns, data

def get_columns():
        return[
                ("Transaction Date") + ":Data:90",
                ("Asset Code") + ":Link/Asset:120",
                ("Asset Name") + ":Data:120",
                ("Source Custodian") + ":Data:120",
                ("Source Cost Center") + ":Data:150",
                ("Target Custodian") + ":Data:120",
                ("Target Cost center") + ":Data:150"
        ]

def get_data(filters):
        query = """select posting_date, asset, asset_name, source_custodian, current_cost_center, target_custodian, target_cost_center from `tabAsset Movement` where docstatus = 1 """
        if filters.get("from_date") and filters.get("to_date"):
                query += " and posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
        return frappe.db.sql(query)

