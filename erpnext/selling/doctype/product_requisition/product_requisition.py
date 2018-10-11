# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document

class ProductRequisition(Document):
	def validate(self):
		if self.start_date > self.end_date:
			frappe.throw("To Date Cannot Be Greater Then From Date")

@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
	def update_so(source, target):
		target.price_list_currency = source.currency
		target.currency = source.currency
		target.plc_conversion_rate = 1
		target.ignore_pricing_rule = 1
		target.run_method("set_missing_values")
		target.run_method("calculate_taxes_and_totals")

        doclist = get_mapped_doc("Product Requisition", source_name,       {
                "Product Requisition": {
                        "doctype": "Sales Order",
                        "field_map": {
				"branch": "branch",
				"customer": "customer",
				"name": "po_no",
				"posting_date":"po_date",
                                "current_resident": "customer_address",
				"location": "shipping_address_name",
				"applicant_name" :"contact_person",
				"currency": "price_list_currency"
                        },
                        "validation": {
                                "docstatus": ["=", 1]
                        }
                },
                "Product Requisition Item": {
                        "doctype": "Sales Order Item",
                        "field_map": [
                                ["item_code", "item_code"],
                                ["qty", "qty"]
                        ],
                }
        }, target_doc, update_so)

        return doclist
