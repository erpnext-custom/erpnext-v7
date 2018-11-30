# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	cond = ''
	if filters.branch:
                cond += " and ml.branch = '{0}'".format(filters.get("branch"))
        if filters.from_date and filters.to_date:
                cond += " and ml.posting_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
	if not cond:
		cond = " and 1 =1"
	query = frappe.db.sql("""
		select *from ( select ml.branch, ml.production_type, ml.posting_date, ml.name
                from
                `tabMarking List` ml  
                where ml.docstatus =1 {0}) as m
                left join
                (select rp.name, rp.journal_entry, rp.total_royalty, rp.marking_list
                from 
		`tabRoyalty Payment` rp 
                where rp.docstatus =1) as r
                on m.name = r.marking_list""".format(cond))
	return query

def get_columns():
	columns = [
		("Branch") + ":Link/Branch:150",
		("Production Type") + "::140",
		("Date") + "::80",
		("Marking List ID") + ":Link/Marking List:120",
	        ("Royalty Payment ID") + ":Link/Royalty Payment:150",
		("Journal Entry") + ":Link/Journal Entry:120",
		("Amount") + ":Currency:140",
	]
	return columns
