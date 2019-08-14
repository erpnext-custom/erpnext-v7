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
                ("Equipment ") + ":Link/Equipment:120",
                ("Equipment No.") + ":Data:120",
                ("Book Type") + ":Data:120",
                ("Fuelbook") + ":Data:120",
		("Supplier") + ":Data:120",
                ("Item Code")+ ":Data:100",
                ("Item Name")+ ":Data:130",
                ("Date") + ":Date:120",
                ("Quantity") + ":Data:100",
                ("Rate") + ":Data:100",
                ("Amount") + ":Currency:120",
		("Cash Memo No") + ":Data:120",
		("POL Slip No") + ":Data:120"
        ]

def get_data(filters):
	cond = "('{0}' between eh.from_date and ifnull(eh.to_date, now()) or '{1}' between eh.from_date and ifnull(eh.to_date, now()))".format(filters.get("from_date"), filters.get("to_date"))
        query =  "select distinct p.equipment, p.equipment_number, p.book_type, p.fuelbook, p.supplier, p.pol_type, p.item_name, p.posting_date, p.qty, p.rate, ifnull(p.total_amount,0), p.memo_number, p.pol_slip_no from tabPOL as p, `tabEquipment History` eh where p.docstatus = 1 and p.equipment = eh.parent and {0}".format(cond)

        if filters.get("branch"):
		query += " and p.branch = \'"+ str(filters.branch) + "\'"

        if filters.get("from_date") and filters.get("to_date"):

                query += " and p.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	if filters.get("direct"):
                query += " and p.direct_consumption = 1"
	else:
		query += " and p.direct_consumption =  p.direct_consumption "
	query += " order by p.posting_date asc"
        return frappe.db.sql(query, debug = 1)
