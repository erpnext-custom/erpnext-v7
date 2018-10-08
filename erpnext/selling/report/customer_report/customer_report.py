# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute(filters=None):
        columns = get_columns(filters)
        data = get_data(filters)
        return columns, data

def get_data(filters):
        cond = " 1= 1"

        if filters.get("dzongkhag"):
                cond += " and dzongkhag = '{0}'".format(filters.get("dzongkhag"))

        if filters.get("from_date") and filters.get("to_date"):
                cond += " and creation between '{0}' and '{1}'".format(filters.from_date, filters.to_date)

	#and customer_group != 'Internal'
        query = frappe.db.sql(""" select name, customer_name, customer_id, customer_type, customer_group, territory, 
                        location, dzongkhag,  date(creation), mobile_no from `tabCustomer`  where {0}  order by name asc""".format(cond), debug =1)
        return query



def get_columns(filters):
        cols = [
                ("Customer ID") + ":Link/Customer:120",
                ("Customer Name") + ":Data:180",
                ("Customer CID") + ":Data:120",
                ("Customer Type") + ":Data:130",
                ("Customer Group") + ":Data:130",
                ("Teritory") + ":Data:100",
                ("Location") + ":Data:120",
                ("Dzongkha") + ":Data:120",
                ("Date of Creation") + ":Date:120",
                ("Contact Number") + ":Data:120"
        ]
        return cols

