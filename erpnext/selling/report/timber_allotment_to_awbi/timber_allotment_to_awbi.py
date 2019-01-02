# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)
        return columns, data


def get_data(filters):
        query = """ select c.name, c.dzongkhag, c.location, c.customer_group, c.mobile_no, pr.allotment_date,
                        pri.qty  from `tabCustomer` c, `tabProduct Requisition` pr, `tabProduct Requisition Item` pri
                        where c.name = pr.customer and pr.is_allotment = 1 and pr.docstatus = 1 and pri.parent = pr.name and c.customer_group = 'AWBI'"""
        if filters.branch:
                query += " and pr.branch = '{0}'".format(filters.get("branch"))
        if filters.from_date and filters.to_date:
                query += " and pr.allotment_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
        if filters.customer: 
                query += " and c.customer_name = '{0}'".format(filters.get("customer"))

        return frappe.db.sql(query)

def get_columns():
        return [
                ("Name of Firm") + ":Link/Customer:190",
                ("Dzongkha") + ":Data:120",
                ("Location") + ":Data:120",
                ("Type Of Industry") + ":Data:120",
                ("Contact No.")+ ":Data:100",
                ("Date of Allotment") + ":Date:120",
                ("Total(Cft)") + ":Float:120",
        ] 


