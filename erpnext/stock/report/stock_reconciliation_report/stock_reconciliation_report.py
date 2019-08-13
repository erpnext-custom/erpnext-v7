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
                ("Doc ID") + ":Link/Stock Reconciliation:120",
                ("Warehouse")+ ":Data:120",
                ("Material Code") + ":Link/Item:120",
                ("Material Name") + ":Data:120",
                ("Current Qty") + ":Data:70",
                ("Current Rate")+ ":Data:70",
                ("Current Total") + ":Data:120",
                ("Qty") + ":Data:70",
                ("Valuation Rate")+ ":Data:70",
                ("Valuation Total") + ":Data:120",
                ("Difference")+ ":Data:100",
      

   ] 
    
def get_data(filters):
        query = """ Select sr.name, sri.warehouse, sri.item_code,  t.item_name, sri.current_qty, sri.current_valuation_rate,round( sri.current_qty*sri.current_valuation_rate, 2) as current_total, sri.qty, sri.valuation_rate, round(sri.qty*sri.valuation_rate,2) as valuation_total,round((sri.current_qty*sri.current_valuation_rate)- (sri.qty*sri.valuation_rate),2) as diff from tabItem as t, `tabStock Reconciliation` as sr, `tabStock Reconciliation Item` as sri where sr.docstatus = 1 and sr.name = sri.parent and t.name = sri.item_code"""
    
        if filters.get("from_date") and filters.get("to_date"):
                query += " and sr.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
        if filters.get("warehouse"):
                query+= " and sri.warehouse = \'" + str(filters.warehouse) + "\' "
        if filters.get("doc_id"):
                query += " and sr.name = \'" + str(filters.doc_id) + "\' "
	
	return frappe.db.sql(query)
import frappe



