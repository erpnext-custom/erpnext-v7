# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint

def execute(filters=None):
	columns = get_columns()
	data = get_data()
	return columns, data

def get_columns():
	return [
		("Particulars") + ":Link/Item:200",
		("Qty Receipt") + ":Float:100",
		("Qty Issued") + ":Float:100",
		("Deployment") + ":Data:250",
		("Individual Report") + ":Data:250"
	]

def get_data():
	data = []
	for d in frappe.db.sql("""
			Select sd.item_name, sd.item_code, s.stock_entry_type, sum(sd.qty) as receipt
			From `tabStock Entry` s
			inner join `tabStock Entry Detail` sd on sd.parent=s.name
			where s.docstatus = 1 and s.stock_entry_type = 'Soelra' and s.purpose = 'Material Receipt'
			group by item_code order by item_code
			""", as_dict=1):
		
		issued = frappe.db.sql("""select sum(sed.qty), sed.s_warehouse
			From `tabStock Entry` ss
			inner join `tabStock Entry Detail` sed on sed.parent=ss.name
			where ss.docstatus = 1 and ss.stock_entry_type = 'Soelra' and ss.purpose = 'Material Issue' and sed.item_code = '{}'""".format(d.item_code))

		desuup = ""
		for i in frappe.db.sql("""
			Select sed.issued_to, sed.issued_to_other, ifnull(sum(sed.qty),0) as qty
			From `tabStock Entry` se
			Inner Join `tabStock Entry Detail` sed On sed.parent = se.name 
			Where se.docstatus = 1 and se.purpose = 'Material Issue' and se.stock_entry_type = 'Soelra' and sed.item_code = '{}'
			group by issued_to, issued_to_other""".format(d.item_code), as_dict=1):
			
			if i.issued_to:
				desuup += i.issued_to  +", Qty: {} <br>".format(i.qty)
			if i.issued_to_other:
				desuup += i.issued_to_other  +", Qty: {} <br>".format(i.qty)

		row=[d.item_name, d.receipt, flt(issued[0][0]), issued[0][1], desuup]
		data.append(row)
	return data