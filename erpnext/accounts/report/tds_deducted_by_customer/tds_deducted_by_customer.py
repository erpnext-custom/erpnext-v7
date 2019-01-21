# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)


	return columns, data

def get_columns():
	return[
		("Branch") + ":Link/Branch:120",
		("Date") + ":Date:120",
		("Invoice Type") + ":Data:120",
		("Invoice No.") + ":Dynamic Link/"+_("Invoice Type")+":120",
		("Customer") + ":Link/Customer:120",
		("Gross Amount")+ ":Currency:120",
		("TDS Amount") + ":Currency:120"
	      ]

def get_data(filters):
	

	query= " select pe.branch, pe.posting_date, 'Sales Invoice', per.reference_name, pe.party, pe.base_total_allocated_amount, pe.tds_amount from `tabPayment Entry` as pe, `tabPayment Entry Reference` as per where per.parent= pe.name and pe.tds_amount != 0 and pe.docstatus=1 {0} union all select pp.branch, pp.posting_date, 'Project Payment', pp.name, pp.party, pp.total_amount, pp.tds_amount from `tabProject Payment` as pp where pp.tds_amount != 0 and pp.docstatus=1 {1} union all select mp.branch, mp.posting_date, 'Mechanical Payment', mp.name, mp.customer, mp.receivable_amount, mp.tds_amount from `tabMechanical Payment` as mp where mp.tds_amount !=0 and mp.docstatus=1 {2} union all select dp.branch, dp.posting_date, 'Direct Payment', dp.name,  dp.party, dp.amount, dp.tds_amount from `tabDirect Payment` as dp where dp.tds_amount !=0 and dp.docstatus=1 and dp.party_type= 'Customer' {3}"
	
	if filters.get("from_date") and filters.get("to_date"):
		cond1 = " and pe.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
		cond2 = " and pp.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
		cond3 = " and mp.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"	
		cond4 = " and dp.posting_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"

	#frappe.msgprint(query)
	return frappe.db.sql(query.format(cond1,cond2,cond3,cond4))
