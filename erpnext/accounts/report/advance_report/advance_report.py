# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	if filters.party_type == "Supplier":
		query = "select supplier_name as party, name, grand_total, advance_paid from `tabPurchase Order` where docstatus = 1"
		if filters.party:
			query += " and supplier_name = '{0}'".format(filters.party)
	else:
		query = "select customer as party, name, grand_total, advance_paid from `tabSales Order` where docstatus = 1"
		if filters.party:
			query += " and customer = '{0}'".format(filters.party)
	
	if filters.item:
		query += " and name = '{0}'".format(filters.item)	
	
	if filters.branch:
		query += " and branch = '{0}'".format(filters.branch)

	if filters.from_date and filters.to_date:
		query += " and transaction_date between '{0}' and '{1}'".format(filters.from_date, filters.to_date)
	
	query += " order by transaction_date "

	data = []
	for a in frappe.db.sql(query, as_dict=1):
		if filters.party:
			row = [a.name, a.grand_total, a.advance_paid, flt(a.grand_total) - flt(a.advance_paid)]	
		else:
			row = [a.party, a.name, a.grand_total, a.advance_paid, flt(a.grand_total) - flt(a.advance_paid)]	
		data.append(row)
	return data

def get_columns(filters):
	if filters.party_type == "Supplier":
		if not filters.party:
			return ["Supplier:Link/Supplier:150", "Purchase Order:Link/Purchase Order:150", "Purchase Amount:Currency:120", "Advance Amount:Currency:120", "Balance Amount:Currency:120"]
		return ["Purchase Order:Link/Purchase Order:150", "Purchase Amount:Currency:120", "Advance Amount:Currency:120", "Balance Amount:Currency:120"]
	else:
		if not filters.party:
			return ["Customer:Link/Customer:150", "Sales Order:Link/Sales Order:150", "Sales Amount:Currency:120", "Advance Amount:Currency:120", "Balance Amount:Currency:120"]
		return ["Sales Order:Link/Sales Order:150", "Sales Amount:Currency:120", "Advance Amount:Currency:120", "Balance Amount:Currency:120"]

