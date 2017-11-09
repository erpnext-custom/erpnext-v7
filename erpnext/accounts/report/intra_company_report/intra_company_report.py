# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	gl = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
	if not gl:
		frappe.throw("Setup Intra-Company Account in Accounts Settings")	
	ccs = frappe.db.sql("select name from `tabCost Center` where is_disabled != 1 and name != %s", filters.cost_center, as_dict=True)
	gls = frappe.db.sql("select a.voucher_no, sum(credit) as credit, sum(debit) as debit, debit_cc, credit_cc from (select credit, voucher_no, cost_center as credit_cc, posting_date from `tabGL Entry` where account = %s and debit = 0) as a JOIN (select debit, voucher_no, cost_center as debit_cc from `tabGL Entry` where account = %s and credit = 0) as b ON a.voucher_no = b.voucher_no and a.posting_date between %s and %s and (credit_cc = %s or debit_cc = %s) group by a.voucher_no", (gl, gl, filters.from_date, filters.to_date, filters.cost_center, filters.cost_center), as_dict=True)
	cc_amount = {}
	for gl in gls:
		if gl.debit_cc.encode('utf-8') == filters.cost_center:
			key = str(gl.credit_cc.encode('utf-8'))
			if not cc_amount.has_key(key):
				cc_amount[key] = {"debit": flt(gl.debit), 'credit': 0}
			else:
				cc_amount[key] = {"debit": cc_amount[key]['debit'] + flt(gl.debit), "credit": cc_amount[key]['credit']}
		else:
			key = str(gl.debit_cc.encode('utf-8'))
			if not cc_amount.has_key(key):
				cc_amount[key] = {"debit": 0, "credit": flt(gl.credit)}
			else:
				cc_amount[key] = {"debit": cc_amount[key]['debit'], "credit": cc_amount[key]['credit'] + flt(gl.credit)}
	for key in cc_amount:
		row = [key]
		#Payable
		if cc_amount[key].has_key('credit'):
			row.append(cc_amount[key]['credit'])
		else:
			 row.append(0)

		#Receivable
		if cc_amount[key].has_key('debit'):
			row.append(cc_amount[key]['debit'])
		else:
			 row.append(0)
		#Balance
		row.append(flt(row[2]) - flt(row[1]))
		data.append(row)
	return data
	
def get_columns():
	return [	
		"Cost Center:Link/Cost Center:230", "Payable:Currency:150", "Receivable:Currency:150", "Balance:Currency:150"
		]	
