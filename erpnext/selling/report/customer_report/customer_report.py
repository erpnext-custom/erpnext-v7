# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute(filters=None):
        columns = get_columns(filters)
        data = get_data(filters)
        return columns, data

def get_data(filters):
        cond = "and 1= 1"

        if filters.get("dzongkhag"):
                cond += " and c.dzongkhag = '{0}'".format(filters.get("dzongkhag"))

        if filters.get("customer"):
                cond += " and c.name = '{0}'".format(filters.get("customer"))
        
        if filters.get("customer_group"):
                cond += " and c.customer_group = '{0}'".format(filters.get("customer_group"))
        
        if filters.get("construction_type"):
                cond += " and sr.construction_type = '{0}'".format(filters.get("construction_type"))
        
        if filters.get("territory"):
                cond += " and c.territory = '{0}'".format(filters.get("territory"))
        
        if filters.get("branch"):
                cond += " and c.branch = '{0}'".format(filters.get("branch"))
        
        if filters.get("item_group"):
                cond += " and soi.item_group = '{0}'".format(filters.get("item_group"))
        
        if filters.get("item_sub_group"):
                cond += " and i.item_sub_group = '{0}'".format(filters.get("item_sub_group"))\
        
        if filters.get("item"):
                cond += " and i.name = '{0}'".format(filters.get("item"))
        
        if filters.get("warehouse"):
                cond += " and soi.warehouse = '{0}'".format(filters.get("warehouse"))

        if filters.get("from_date") and filters.get("to_date"):
                cond += " and c.creation between '{0}' and '{1}'".format(filters.from_date, filters.to_date)

	# and customer_group != 'Internal'
        if not filters.aggregate:
                query = frappe.db.sql(""" select c.customer_name, c.customer_id, c.customer_group, sr.construction_type, sum(soi.qty), sum(soi.delivered_qty), c.branch, c.territory,
                        c.location, c.dzongkhag, soi.item_name, soi.item_group,i.item_sub_group, soi.warehouse, date(c.creation), c.mobile_no from `tabCustomer` c left join `tabSite Registration` sr on c.customer_id = sr.user, `tabItem` i, `tabSales Order` so, `tabSales Order Item` soi where so.customer = c.name and so.name = soi.parent and soi.item_code = i.name and so.docstatus = 1 {0} group by c.customer_name, soi.warehouse order by c.name asc""".format(cond), debug =1)
        else:
                query = frappe.db.sql(""" select c.customer_name, so.name, c.location, soi.item_group, i.item_sub_group,  sum(soi.qty), sum(soi.delivered_qty) from `tabCustomer` c, `tabItem` i, `tabSales Order` so, `tabSales Order Item` soi where so.customer = c.name and so.name = soi.parent and soi.item_code = i.name and so.docstatus = 1 {0} group by c.customer_name order by c.name asc""".format(cond), debug =1)

        return query



def get_columns(filters):
        if filters.aggregate:
                cols = [
                        ("Customer Name") + ":Data:180",
                        ("Sales Order") + ":Link/Sales Order:120",
                        ("Location") + ":Data:120",
                        ("Material Group") + ":Data:120",
                        ("Material Sub Group") + ":Data:120",
                        ("Sales Order Quantity") + ":Float:120",
                        ("Delivered Quantity") + ":Float:120",
                        
                ]
        else:
                cols = [
                        ("Customer Name") + ":Data:180",
                        ("Customer CID") + ":Data:120",
                        ("Customer Group") + ":Data:130",
                        ("Construction Type") + ":Data:130",
                        ("Quantity Approved") + ":Float:130",
                        ("Quantity Delivered") + ":Float:130",
                        ("Branch/Unit") + ":Data:130",
                        ("Region") + ":Data:100",
                        ("Location") + ":Data:120",
                        ("Dzongkhag") + ":Data:120",
                        ("Material") + ":Data:120",
                        ("Material Group") + ":Data:120",
                        ("Material Sub Group") + ":Data:120",
                        ("Warehouse") + ":Data:120",
                        ("Date of Creation") + ":Date:120",
                        ("Contact Number") + ":Data:120"
                ]
        return cols

