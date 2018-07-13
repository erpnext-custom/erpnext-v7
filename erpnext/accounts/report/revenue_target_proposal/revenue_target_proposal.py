# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns, grand_total_dict = get_columns(filters)
	data = get_data(filters, grand_total_dict)
	return columns, data

def get_data(filters, grand_total):
	data = []
	cc_amount = {}
	all_data = frappe.db.sql("select ra.account, ra.account_code, ra.cost_center, ra.net_target_amount as target_amount from `tabRevenue Target Account` ra, `tabRevenue Target` rt where ra.parent = rt.name and rt.fiscal_year = %s order by ra.account_code", filters.fiscal_year, as_dict=True) 
	#frappe.msgprint("{0}".format(all_data))
	for a in all_data:
		acc = str(a.account).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')
		cc = str(a.cost_center).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')
		if cc_amount.has_key(acc):
			cc_amount[acc][cc] = a.target_amount
		else:
			row = {"account": str(a.account), "account_code": str(a.account_code), cc: a.target_amount}
			cc_amount[acc] = row;

	for a in cc_amount:
		row = {}
		total = 0
		for b in cc_amount[a]:
			row[b] = cc_amount[a][b]
			if b not in ('account','account_code'):
				total = flt(total) + flt(cc_amount[a][b])
		row['total'] = flt(total)
		data.append(row)
	data.append(grand_total)
	return data

def get_columns(filters):
	gtot = 0.0
	total_dict = {"account_code": "Total"}
	cols = [
		{
			"fieldname": "account",
			"label": "Account",
			"fieldtype": "Link",
			"options": "Account",
			"width": 300
		},
		{
			"fieldname": "account_code",
			"label": "Account Code",
			"fieldtype": "Data",
			"width": 100
		},
	]
	ccs = frappe.db.sql("select ra.cost_center, sum(ra.net_target_amount) as grand_total from `tabRevenue Target Account` ra, `tabRevenue Target` rt where ra.parent = rt.name and rt.docstatus < 2 and rt.fiscal_year = %s group by ra.cost_center order by ra.cost_center ASC", filters.fiscal_year, as_dict=True)
	for cc in ccs:
		cc_key = str(cc.cost_center).rstrip(" - CDCL").replace(' ', '_').strip().lower().encode('utf-8')
		row = {}
		row['fieldname'] = cc_key
		row['label'] = cc.cost_center
		row['fieldtype'] = "Currency"
		row['width'] = 180
		cols.append(row)
		total_dict[cc_key] = flt(cc.grand_total)
		gtot += flt(cc.grand_total)
	cols.append({"fieldname": "total", "label": "Total", "fieldtype": "Currency", "width": 180})
	total_dict['total'] = flt(gtot)
	#frappe.msgprint(_("{0}").format(total_dict))
	return cols, total_dict
