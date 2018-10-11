# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns(filters)
        data = get_data(filters)

        return columns, data

def get_columns(filters):
        if filters.uinput == "Returned":
                cols= [
                        ("Purchase Reciept #") + ":Link/Purchase Receipt:120",
                        ("Branch.") + ":Data:120",
                        ("Date") + ":Date:100",
                        ("Supplier ") + ":Data:180",
                        ("Item Code.") + ":Data:120",
                        ("Item Name") + ":Data:170",
                        ("UoM") + ":Data:70",
                        ("Returned Qty") + ":Int:90",
                        ("Rate") + ":Currency:100",
                        ("Amount") + ":Currency:120",
                        ]
        else:
               cols= [
                        ("Purchase Reciept #") + ":Link/Purchase Receipt:120",
                        ("Branch.") + ":Data:120",
                        ("Date") + ":Date:100",
                        ("Supplier ") + ":Data:180",
                        ("Item Code.") + ":Data:120",
                        ("Item Name") + ":Data:170",
                        ("UoM") + ":Data:70",
                        ("Rejected Qty") + ":Int:90",
                        ("Rate") + ":Currency:100",
                        ("Amount") + ":Currency:120",
                       ]
	return cols

def get_data(filters):
        if filters.uinput == "Rejected":
                query = """ select pr.name, pr.branch, pr.posting_date, pr.supplier,  pri.item_code,
                                pri.item_name, pri.uom, pri.rejected_qty, pri.rate, pri.rejected_qty*pri.rate as amount
                                from `tabPurchase Receipt Item`  pri, `tabPurchase Receipt` as pr
                                where pri.parent = pr.name
                                and pri.docstatus = 1 """
        else:
		query = """ select pr.name, pr.branch, pr.posting_date, pr.supplier,  pri.item_code,
                                pri.item_name, pri.uom, pri.received_qty, pri.rate, pri.received_qty*pri.rate as amount
                                from `tabPurchase Receipt Item`  pri, `tabPurchase Receipt` as pr
                                where pri.parent = pr.name
                                and pr.is_return = '1' """


	if filters.get("branch"):
                query += " and pr.branch = \'"+ str(filters.branch) + "\'"

        if filters.get("from_date") and filters.get("to_date"):
                query += " and pr.posting_date between \'"+ str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

        return frappe.db.sql(query)

