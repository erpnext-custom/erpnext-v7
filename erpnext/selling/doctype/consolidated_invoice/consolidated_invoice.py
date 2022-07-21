# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

class ConsolidatedInvoice(Document):
	def on_cancel(self):
		if self.payment_entry:
			pe = frappe.get_doc("Payment Entry",self.payment_entry)
			if pe.docstatus != 2:
				frappe.throw("""Payment Entry <b><a href="#Form/Payment%20Entry/{0}">{0}</a></b> linked with this Consolidated Invoice which is not cancelled.""".format(self.payment_entry))

@frappe.whitelist()
def get_invoices(from_date, to_date, customer, cost_center):
	# frappe.msgprint(str(frappe.db.sql("select si.name, si.sales_invoice_date as posting_date, si.outstanding_amount, sii.delivery_note, sii.sales_order, sii.accepted_qty from `tabSales Invoice` si, `tabSales Invoice Item` sii where si.docstatus = 1 and si.outstanding_amount > 0 and si.sales_invoice_date between %s and %s and sii.sales_order = %s and sii.parent = si.name and not exists (select 1 from `tabConsolidated Invoice Item` ci where ci.invoice_no = si.name and ci.docstatus = 1) order by posting_date", (from_date, to_date, sales_order), as_dict=True)))
	return frappe.db.sql("""select si.name, sii.sales_order, si.sales_invoice_date as posting_date, si.due_date, 
				sum(sii.qty) as qty, sum(sii.base_amount) as cost_of_goods,
				(select dn.transportation_charges from `tabDelivery Note` dn where dn.name = sii.delivery_note),
				(select dn.loading_cost from `tabDelivery Note` dn where dn.name = sii.delivery_note),
				(select dn.challan_cost from `tabDelivery Note` dn where dn.name = sii.delivery_note),
				si.outstanding_amount, sii.delivery_note, sii.sales_order, sii.accepted_qty 
			from `tabSales Invoice` si, `tabSales Invoice Item` sii 
			where si.docstatus = 1 and si.outstanding_amount > 0 
			and si.sales_invoice_date between %s and %s 
			and si.customer = %s and sii.parent = si.name 
			and not exists (select 1 from `tabConsolidated Invoice Item` ci 
							where ci.invoice_no = si.name and ci.docstatus = 1) 
			and si.branch = (select b.name from `tabBranch` b where b.cost_center = %s) 
			group by si.name order by posting_date""", (from_date, to_date, customer, cost_center), as_dict=True)

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None): 
	def set_missing_values(source, target):
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_account_details
		target.naming_series = "Journal Voucher"
		target.branch = frappe.db.get_value("Branch",{"cost_center":source.cost_center},"name")
		target.payment_type = "Receive"
		target.party_type = "Customer"
		target.party = source.customer
		target.actual_receivable_amount = source.total_amount
		target.total_amount = source.total_amount
		target.paid_amount = source.total_amount
		target.total_allocated_amount = source.total_amount
		target.consolidated_invoice_id = source.name
		target.paid_from = source.debit_to
		target.paid_to = frappe.db.get_value("Branch",frappe.db.get_value("Branch",{"cost_center":source.cost_center},"name"),"revenue_bank_account")
		if source.debit_to:
			acc = get_account_details(source.debit_to, source.posting_date)
			target.paid_from_account_currency = acc.account_currency
			target.paid_from_account_balance = acc.account_balance
		if source.customer:
			target.customer_dzongkhag = frappe.db.get_value("Customer",source.customer,"dzongkhag")
			target.customer_location = frappe.db.get_value("Customer",source.customer,"location")
		target.pl_cost_center = source.cost_center
		if len(source.items) > 0:
			for a in source.items:
				row = target.append("references",{})
				row.reference_doctype = "Sales Invoice"
				row.reference_name = a.invoice_no
				row.due_date = frappe.db.get_value("Sales Invoice",a.invoice_no,"due_date")
				row.total_amount = flt(a.amount)
				row.outstanding_amount = flt(a.amount)
				row.allocated_amount = flt(a.amount)
				row.exchange_rate = 1

		# target.run_method("calculate_taxes_and_totals")

	def update_item(source, target, source_parent):
		pass
		# target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.base_rate)
		# target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
		# target.qty = flt(source.qty) - flt(source.delivered_qty)
		# expense_account,is_prod = frappe.db.get_value("Item", source.item_code, ["expense_account", "is_production_item"])
		# if is_prod:
		# 	expense_account = get_settings_value("Production Account Settings", source_parent.company, "default_production_account")
		# 	if not expense_account:
		# 		frappe.throw("Setup Default Production Account in Production Account Settings")
		# target.expense_account = expense_account

	target_doc = get_mapped_doc("Consolidated Invoice", source_name, {
		"Consolidated Invoice": {
			"doctype": "Payment Entry",
			"field_map": {
				"total_amount": "actual_receivable_amount",
				"total_amount": "total_amount" ,
				"total_amount": "paid_amount",
				"total_amount":	"total_allocated_amount"
			},
			"validation": {
				"docstatus": ["=", 1]
			}
		}
	}, target_doc, set_missing_values)

	return target_doc