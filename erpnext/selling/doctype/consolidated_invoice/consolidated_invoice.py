# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ConsolidatedInvoice(Document):
	pass

@frappe.whitelist()
def get_invoices(from_date, to_date, item_code, customer, cost_center):
	return frappe.db.sql("select si.name, si.sales_invoice_date as posting_date, si.outstanding_amount, sii.delivery_note, sii.sales_order, sii.accepted_qty from `tabSales Invoice` si, `tabSales Invoice Item` sii where si.docstatus = 1 and si.outstanding_amount > 0 and si.customer = %s and sii.cost_center = %s and si.sales_invoice_date between %s and %s and sii.item_code = %s and sii.parent = si.name and not exists (select 1 from `tabConsolidated Invoice Item` ci where ci.invoice_no = si.name and ci.docstatus = 1) order by posting_date", (customer, cost_center, from_date, to_date, item_code), as_dict=True)
