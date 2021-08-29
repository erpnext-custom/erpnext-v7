# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)
        return columns, data


def get_data(filters):
        query = """ select c.name, c.dzongkhag, c.location, c.customer_group, c.mobile_no, so.allotment_date,
soi.qty  from `tabCustomer` c, `tabSales Order` so, `tabSales Order Item` soi
where c.name = so.customer and soi.parent = so.name and c.customer_group  = 'AWBI' and so.docstatus = 1 """
        if filters.branch:
                query += " and so.branch = '{0}'".format(filters.branch)
        # if filters.from_date and filters.to_date:
        #         query += " and so.allotment_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
        if filters.customer: 
                query += " and c.customer_name = '{0}'".format(filters.get("customer"))
        # frappe.msgprint(query)
        return frappe.db.sql(query, as_dict=True)
        # frappe.msgprint(str(data))
        # return data

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


