# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class StockPriceTemplate(Document):
	pass

#select stock entry templates based on dates
@frappe.whitelist()
def get_template_list(doctype, txt, searchfield, start, page_len, filters): 
	if filters['naming_series']:
		query = "SELECT name, template_name FROM `tabStock Price Template` WHERE \'" + filters['posting_date'] +"\'  BETWEEN from_date AND to_date AND naming_series = \'" + filters['naming_series'] + "\' and docstatus = 1 and purpose= \'"+ filters['purpose'] +"\'";
		return frappe.db.sql(query);
	

#Get item values from "Initial Stock Templates" during stock entry
@frappe.whitelist()
def get_initial_values(name):
	result = frappe.db.sql("SELECT a.item_code, a.item_name, a.uom, a.rate_currency, a.rate_amount, b.expense_account, b.selling_cost_center, b.stock_uom FROM `tabStock Price Template` AS a, tabItem AS b WHERE a.item_name = b.item_name AND a.name = \'" + str(name) + "\'", as_dict=True);
	return result;
