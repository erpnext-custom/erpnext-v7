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
                
		("Branch") + ":Link/Branch: 120",
		("Customer") + ":Link/Customer: 150",
		("Item") + ":Link/Item:80",
                ("Item Name") + ":Data:120",
		("Invoice Date") + ":Date:80",
                ("Quantity") + ":Float:80",
                ("UoM") + ":Data:50",
                ("Rate") + ":Currency:80",
		("Billed Amount") + ":Currency:120",
                ("Received Amount") + ":Currency:120",
                ("Receiveable Amount") + ":Currency:120",
        ]

def get_data(filters):
        query = """ select p.branch, p.customer, c.item, c.item_name, p.posting_date, c.qty, c.uom, c.rate, c.amount,
	case p.paid
	when p.paid = 1 then c.amount else 0.0 end as paid,
	case p.paid
	when p.paid = 0 then c.amount else 0.0 end as receiv
	 from `tabInvoice` p, `tabInvoice Item` c
	where c.parent = p.name and p.docstatus = 1"""

        if filters.get("branch"):
                query += " and p.branch = \'"+ str(filters.get("branch")) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and p.posting_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
	return frappe.db.sql(query)
