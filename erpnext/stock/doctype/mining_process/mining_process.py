# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MiningProcess(Document):
	pass

@frappe.whitelist()
def get_item_details(item_code): 
	if item_code:
            return frappe.db.sql("select item_name, stock_uom from `tabItem` where item_code = " + str(item_code), as_dict=True)

