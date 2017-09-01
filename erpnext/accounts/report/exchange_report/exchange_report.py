# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_columns():
	columns = [
	("Date") + ":date:120",
	("Rate(Nu.)") + ":currency:120",
	]

	return columns

def get_data(filters):
	data  = "select erh.date, erh.exchange_rate FROM `tabExchange Rate History` as erh WHERE docstatus = 1"

	if filters.get("from_date") and filters.get("to_date"):
		data += " and erh.date  between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	if filters.get("currency"):
		data += " and erh.from_currency = \'" + str(filters.currency) + "\'"
	return frappe.db.sql(data)
