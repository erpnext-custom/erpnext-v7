# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt

class ConsolidatedInvoice(Document):
	def on_update(self):
		self.set_total_amount()
		self.check_duplicate_entries()

	def on_cancel(self):
		if self.payment_entry:
			pes = str(self.payment_entry).split(", ")
			for a in pes:
				pe = frappe.get_doc("Payment Entry",a)
				if pe.docstatus != 2:
					frappe.throw("""Payment Entry <b><a href="#Form/Payment%20Entry/{0}">{0}</a></b> linked with this Consolidated Invoice which is not cancelled.""".format(a))

	def check_partial_pe(self):
		total_amount = 0
		show_button = 0
		for a in self.items:
			total_amount += flt(a.amount,2)
		paid_amount = frappe.db.sql("""
			select sum(ifnull(paid_amount,0)) from `tabPayment Entry` where consolidated_invoice_id = '{}' and docstatus < 2
        """.format(self.name))[0][0]
		if total_amount != flt(paid_amount,2):
			show_button = 1
		return show_button

	def set_total_amount(self):
		self.total_amount = self.quantity = 0
		for row in self.items:
			self.total_amount += flt(row.amount,2)
			self.quantity += flt(row.accepted_qty)

	def check_duplicate_entries(self):
		for i in self.get("items"):
			for d in frappe.db.get_all("Consolidated Invoice Item", {"invoice_no": i.invoice_no, "parent": ("!=",self.name),
						"docstatus": ("!=", 2)}, ["parent"]):
				frappe.throw(_("Row#{}: {} is already pulled in {}").format(i.idx, frappe.get_desk_link("Sales Invoice", i.invoice_no),
					frappe.get_desk_link("Consolidated Invoice", d.parent)))

@frappe.whitelist()
def get_invoices(name, from_date, to_date, customer, cost_center):
	if from_date and to_date and to_date < from_date:
		frappe.throw(_("<b>From Date</b> should be less than or equal to <b>To Date</b>"))

	invoices = frappe.db.sql("""select si.name, sii.sales_order, si.sales_invoice_date as posting_date, si.due_date, 
				sum(sii.qty) as qty, sum(sii.accepted_qty) as accepted_qty, sum(sii.base_amount) as cost_of_goods,
				max(dn.transportation_charges) transportation_charges,
				max(dn.loading_cost) loading_cost,
				max(dn.challan_cost) challan_cost,
				sum(sii.base_net_amount) amount, sii.delivery_note 
			from `tabSales Invoice` si
			inner join `tabSales Invoice Item` sii on sii.parent = si.name
			left join `tabDelivery Note` dn on dn.name = sii.delivery_note
			where si.docstatus = 1 
			and si.outstanding_amount > 0 
			and si.sales_invoice_date between %(from_date)s and %(to_date)s 
			and si.customer = %(customer)s
			and not exists (select 1 from `tabConsolidated Invoice Item` ci 
							where ci.invoice_no = si.name and ci.docstatus != 2
							and ci.parent != %(name)s) 
			and si.branch = (select b.name from `tabBranch` b where b.cost_center = %(cost_center)s) 
			group by si.name, sii.sales_order, si.sales_invoice_date, si.due_date, sii.delivery_note
			order by posting_date""", ({"from_date": from_date, "to_date": to_date,
					"customer": customer, "cost_center": cost_center, "name": name}), as_dict=True)
	if not invoices:
		frappe.throw(_("There are no invoices found for the selected period"), title="No Data Found")
	return invoices

@frappe.whitelist()
def make_payment_entry(source_name, target_doc=None): 
	def set_missing_values(source, target):
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_account_details
		exclude = []
		target.naming_series = "Journal Voucher"
		target.branch = frappe.db.get_value("Branch",{"cost_center":source.cost_center},"name")
		target.payment_type = "Receive"
		target.party_type = "Customer"
		target.party = source.customer
		target.actual_receivable_amount = source.total_amount
		target.consolidated_invoice_id = source.name
		target.paid_from = source.debit_to
		target.paid_to = frappe.db.get_value("Branch",frappe.db.get_value("Branch",{"cost_center":source.cost_center},"name"),"revenue_bank_account")
		acc_to = get_account_details(frappe.db.get_value("Branch",frappe.db.get_value("Branch",{"cost_center":source.cost_center},"name"),"revenue_bank_account"), source.posting_date)
		target.paid_to_account_currency = acc_to.account_currency
		target.paid_to_account_balance = acc_to.account_balance
		if source.debit_to:
			acc = get_account_details(source.debit_to, source.posting_date)
			target.paid_from_account_currency = acc.account_currency
			target.paid_from_account_balance = acc.account_balance
		if source.customer:
			target.customer_dzongkhag = frappe.db.get_value("Customer",source.customer,"dzongkhag")
			target.customer_location = frappe.db.get_value("Customer",source.customer,"location")
		# excluded = frappe.db.sql("""
		# 	select per.reference_name from `tabPayment Entry Reference` per, `tabPayment Entry` pe where per.parent = pe.name and pe.consolidated_invoice_id = '{}'
		# 	and pe.docstatus < 2
        # """)
		# paid_amount = frappe.db.sql("""
		# 	select sum(ifnull(pe.paid_amount,0)) from `tabPayment Entry` pe where pe.consolidated_invoice_id = '{}'
		# 	and pe.docstatus = 1
        # """.format(source.name))[0][0]
		# if excluded:
		# 	for a in excluded:
		# 		exclude.append(a)
		target.pl_cost_center = source.cost_center
		total_amount = outstanding_amount = 0
		if len(source.items) > 0:
			for a in source.items:
				# if a.invoice_no not in exclude:
				allocated_amount = frappe.db.sql("""
					select sum(ifnull(per.allocated_amount,0)) from `tabPayment Entry` pe, `tabPayment Entry Reference` per where per.parent = pe.name and pe.consolidated_invoice_id = '{}'
					and pe.docstatus = 1 and per.reference_name = '{}'
        		""".format(source.name, a.invoice_no))[0][0]
				if flt(a.amount,2) > flt(allocated_amount,2):
					row = target.append("references",{})
					row.reference_doctype = "Sales Invoice"
					row.reference_name = a.invoice_no
					row.due_date = frappe.db.get_value("Sales Invoice",a.invoice_no,"due_date")
					row.total_amount = flt(a.amount,2) - flt(allocated_amount, 2)
					row.outstanding_amount = flt(a.amount,2) - flt(allocated_amount, 2)
					row.allocated_amount = flt(a.amount,2) - flt(allocated_amount, 2)
					row.exchange_rate = 1
					total_amount += flt(row.total_amount,2)
					outstanding_amount += flt(a.amount,2) - flt(allocated_amount, 2)
		target.total_amount = flt(total_amount,2)
		target.paid_amount = flt(total_amount,2)
		target.total_allocated_amount = flt(total_amount,2)
		target.actual_amount = flt(total_amount,2)
		target.outstanding_amount = flt(a.amount,2) - flt(allocated_amount, 2)

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