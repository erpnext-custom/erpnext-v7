# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, grand_total_dict = get_columns(filters)
	data = get_data(filters, grand_total_dict) 
	return columns, data

def get_data(filters, grand_total):
	data = []
	cc_amount = {}
	all_data = frappe.db.sql("select b.cost_center, a.account, a.budget_amount from `tabBudget Account` a, tabBudget b where a.parent = b.name and b.docstatus = 0 and b.fiscal_year = %s", filters.fiscal_year, as_dict=True)
	for a in all_data:
		acc = str(a.account).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')	
		cc = str(a.cost_center).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')	
		if cc_amount.has_key(acc):
			cc_amount[acc][cc] = a.budget_amount
		else:
			row = {"account": str(a.account), cc: a.budget_amount}
			cc_amount[acc] = row;

	for a in cc_amount:
		row = {}
		total = 0
		for b in cc_amount[a]:
			row[b] = cc_amount[a][b]
			total = flt(total) + flt(cc_amount[a][b])
		row['total'] = flt(total)
		data.append(row)
	data.append(grand_total)
	return data

def get_columns(filters):
	total_dict = {"account": "Total"}
	cols = [
		{
			"fieldname": "account",
			"label": "Account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 300
		}
	]
	ccs = frappe.db.sql("select b.cost_center, sum(a.budget_amount) as grand_total from `tabBudget Account` a, tabBudget b where a.parent = b.name and b.docstatus = 0 and b.fiscal_year = %s group by b.cost_center order by b.cost_center ASC", filters.fiscal_year, as_dict=True)
	for cc in ccs:
		cc_key = str(cc.cost_center).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')	
		row = {}
		row['fieldname'] = cc_key
		row['label'] = cc.cost_center
		row['fieldtype'] = "Currency"
		row['width'] = 180
		cols.append(row)
		total_dict[cc_key] = flt(cc.grand_total)
	cols.append({"fieldname": "total", "label": "Total", "fieldtype": "Currency", "width": 180})
	return cols, total_dict

