# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	cols, data = get_data(filters)
	return cols, data	
		
def get_data(filters):
	cols = column()
	cond = ''
	if filters.get("from_date") and filters.get("to_date"):
		cond += " and sq.transaction_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
	if filters.get("supplier"):
		cond += " and sq.supplier = '{0}'".format(filters.get("supplier"))

	data = []
	row = {}
	li = []
	item_query = """ select item_code, concat(item_code, ':', item_name) as naa, qty, uom  from `tabRequest for Quotation Item` where parent = '{0}' order by item_code asc""".format(filters.get("rfq"))
	for i in frappe.db.sql(item_query, as_dict =1):
		query =  frappe.db.sql(""" select sq.supplier, sq.transaction_date, sqi.item_code, sqi.item_name, sqi.qty, sqi.uom, 
                        sqi.request_for_quotation, sqi.rate, sqi.amount from `tabSupplier Quotation` sq, `tabSupplier Quotation Item` sqi 
                        where sqi.parent = sq.name and sq.docstatus = 1 and sqi.request_for_quotation = '{0}' and sqi.item_code = '{1}' {2} 
			order by sqi.amount asc""".format(filters.get("rfq"), i.item_code, cond), as_dict =1)
		row = {
                        "item_code": i.naa, "uom": i.uom, "qty": i.qty
                        }
		for d in query:
			if not d:
  	                      frappe.msgpring("Suppler Quotation Not Created for this RFQ")

			if d.supplier not in li:
				li.append(d.supplier)
				cols.append({
				  "fieldname": str(d.supplier).lower(),
				  "label": format(str(d.supplier)),
				  "fieldtype": "Currency",
				  "width": 190
				})
			row[str(d.supplier).lower()]  = str(d.rate)
		data.append(row)
	return cols, tuple(data)

def column():
	columns = [
	{
	  "fieldname": "item_code",
	  "label": "Item Code",
	  "fieldtype": "Link",
	  "options": "Item",
	  "width": 150
	},
	{
          "fieldname": "uom",
          "label": "UOM",
          "fieldtype": "Link", 
          "options": "UOM",
          "width": 80
        },
	{
          "fieldname": "qty",
          "label": "QTY.",
          "fieldtype": "float",
          "width": 60
        }
	]

	return columns
