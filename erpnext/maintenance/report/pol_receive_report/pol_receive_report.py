# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns(filters)
        data = get_data(filters)

        return columns, data
    
def get_columns(filters):
	if not filters.get("own_cc"):
		return [
			("Equipment ") + ":Link/Equipment:120",
			("Equipment No.") + ":Data:120",
			("Book Type") + ":Data:120",
			("Fuelbook") + ":Data:120",
			("Received From") + ":Link/Branch:120",
			("Supplier") + ":Data:120",
			("Item Code")+ ":Data:100",
			("Item Name")+ ":Data:170",
			("Date") + ":Date:120",
			("Quantity") + ":Data:120",
			("Rate") + ":Data:120",
			("Amount") + ":Currency:120"
		]
	else:
		return [
			("Equipment ") + ":Link/Equipment:120",
			("Equipment No.") + ":Data:120",
			("Book Type") + ":Data:120",
			("Fuelbook") + ":Data:120",
			("Supplier") + ":Data:120",
			("Item Code")+ ":Data:100",
			("Item Name")+ ":Data:170",
			("Date") + ":Date:120",
			("Quantity") + ":Data:120",
			("Rate") + ":Data:120",
			("Amount") + ":Currency:120"
		]

def get_data(filters):

	if not filters.get("own_cc"):
		query =  "select p.equipment, p.equipment_number, p.book_type, p.fuelbook, p.fuelbook_branch, p.supplier, p.pol_type, p.item_name, p.posting_date, p.qty, p.rate, ifnull(p.total_amount,0) from tabPOL as p where p.docstatus = 1"
	else:
		query =  "select p.equipment, p.equipment_number, p.book_type, p.fuelbook, p.supplier, p.pol_type, p.item_name, p.posting_date, p.qty, p.rate, ifnull(p.total_amount,0) from tabPOL as p where p.docstatus = 1"

        if filters.get("branch"):
		query += " and p.branch = \'"+ str(filters.branch) + "\'"

        if filters.get("from_date") and filters.get("to_date"):
                query += " and p.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	if filters.get("direct"):
                query += " and p.direct_consumption = 1"
	
	if filters.get("own_cc"):
                query += " and p.fuelbook_branch  = p.equipment_branch"
	query += " order by p.equipment"
        return frappe.db.sql(query)
