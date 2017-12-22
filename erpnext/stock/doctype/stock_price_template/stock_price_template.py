# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _

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

#Get item rates
@frappe.whitelist()
def get_item_rate(tran_type, item_code, tran_date):
        if tran_type == 'Sales':
                table_name = 'tabStock Price Template Item'
        elif tran_type == 'COP':
                table_name = 'tabStock Price Template Buying'
        else:
                frappe.throw(_("Transaction should be eaither of COP or Sales."),title="Wrong Transaction")
                
        result = frappe.db.sql("""
                        select
                                a.item_code,
                                a.item_name,
                                a.uom,
                                a.rate_currency,
                                i.rate,
                                b.expense_account,
                                b.selling_cost_center,
                                b.stock_uom
                        from
                                `tabStock Price Template` as a,
                                `{0}` as i,
                                `tabItem` as b
                        where a.item_code = '{1}'
                        and b.name = a.item_code
                        and i.parent = a.name
                        and '{2}' between i.from_date and ifnull(i.to_date, now())
                        """.format(table_name, item_code, tran_date), as_dict=True)

        if result:
                if len(result) > 1:
                        frappe.throw(_("{0}: Multiple rates found for the given date.").format(item_code), title="Too Many Values Found")
                else:
                        return result
        else:
                frappe.throw(_("Please define '{0}' rate in Selling -> COP/Sales Price Template.").format(tran_type),title="No Data Found")
