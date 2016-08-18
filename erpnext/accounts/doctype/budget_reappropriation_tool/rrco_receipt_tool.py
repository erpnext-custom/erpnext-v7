# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.model.document import Document


class RRCOReceiptTool(Document):
	pass


@frappe.whitelist()
def get_invoices(start_date=None, end_date=None, tds_rate=2):
	attendance_not_marked = []
	attendance_marked = []
	query = "select name, posting_date, bill_no FROM `tabPurchase Invoice` AS a WHERE outstanding_amount = 0 AND posting_date BETWEEN \'" + str(start_date) + "\' AND \'" + str(end_date) + "\' AND tds_rate = " + str(tds_rate) + " AND NOT EXISTS (SELECT 1 FROM `tabRRCO Receipt Entries` AS b WHERE b.purchase_invoice = a.name);"
	invoice_list = frappe.db.sql(query, as_dict=True);

	return {
		"marked": attendance_marked,
		"unmarked": invoice_list 
	}


@frappe.whitelist()
def mark_invoice(invoice_list=None, receipt_number=None, receipt_date=None, cheque_number=None, cheque_date=None):
	invoice_list = json.loads(invoice_list)
	for invoice in invoice_list:
		rrco = frappe.new_doc("RRCO Receipt Entries")
		rrco.purchase_invoice = invoice['name']
		rrco.receipt_date = str(receipt_date)
		rrco.receipt_number = str(receipt_number)
		rrco.cheque_number = str(cheque_number)
		rrco.cheque_date = str(cheque_date)
		rrco.submit()
