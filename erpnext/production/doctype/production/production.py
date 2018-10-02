# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate, nowtime, getdate
from erpnext.accounts.utils import get_fiscal_year
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, check_budget_available
from erpnext.controllers.stock_controller import StockController
from erpnext.stock.utils import get_stock_balance

class Production(StockController):
	def validate(self):
		check_future_date(self.posting_date)
		self.check_cop()
		self.validate_warehouse()
		self.validate_items()
		self.validate_posting_time()

	def validate_warehouse(self):
		self.validate_warehouse_branch(self.warehouse, self.branch)

	def validate_items(self):
		prod_items = self.get_production_items()
		for item in self.get("raw_materials"):
			if item.item_code not in prod_items:
				frappe.throw(_("{0} is not a Production Item").format(item.item_code))
			if flt(item.qty) <= 0:
				frappe.throw(_("Quantity for <b>{0}</b> cannot be zero or less").format(item.item_code))

		for item in self.get("items"):
			if item.item_code not in prod_items:
				frappe.throw(_("{0} is not a Production Item").format(item.item_code))
			if flt(item.qty) <= 0:
				frappe.throw(_("Quantity for <b>{0}</b> cannot be zero or less").format(item.item_code))
			if flt(item.cop) <= 0:
				frappe.throw(_("COP for <b>{0}</b> cannot be zero or less").format(item.item_code))

	def check_cop(self):
		for a in self.items:
			branch = frappe.db.sql("select 1 from `tabCOP Branch` where parent = %s and branch = %s", (a.price_template, self.branch))
			if not branch:
				frappe.throw("Selected COP is not defined for your Branch")

			cop = frappe.db.sql("select cop_amount from `tabCOP Rate Item` where parent = %s and item_sub_group = %s", (a.price_template, str(frappe.db.get_value("Item", a.item_code, "item_sub_group"))), as_dict=1)
			if not cop:
				frappe.throw("COP Rate is not defined for your Item")
			a.cop = cop[0].cop_amount

	def on_submit(self):
		self.check_cop()
		self.assign_default_dummy()
		self.make_products_sl_entry()
		self.make_products_gl_entry()
		self.make_raw_material_stock_ledger()
		self.make_raw_material_gl_entry()
		self.make_production_entry()

	def on_cancel(self):
		self.assign_default_dummy()
		self.make_products_sl_entry()
		self.make_products_gl_entry()
		self.make_raw_material_stock_ledger()
		self.make_raw_material_gl_entry()
		self.delete_production_entry()

	def assign_default_dummy(self):
		self.pol_type = None
		self.stock_uom = None 

	def make_products_sl_entry(self):
		sl_entries = []

		for a in self.items:
			sl_entries.append(prepare_sl(self,
				{
					"stock_uom": a.uom,
					"item_code": a.item_code,
					"actual_qty": a.qty,
					"warehouse": self.warehouse,
					"incoming_rate": flt(a.cop, 2)
				}))

		if sl_entries: 
			if self.docstatus == 2:
				sl_entries.reverse()

			self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')


	def make_products_gl_entry(self):
		gl_entries = []

		wh_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": self.warehouse}, "name")
		if not wh_account:
			frappe.throw(str(self.warehouse) + " is not linked to any account.")

		expense_account = frappe.db.get_value("Production Account Settings", self.company, "default_production_account")
		if not expense_account:
                        frappe.throw("Setup Default Production Account in Production Account Settings")

		for a in self.items:
			amount = flt(a.qty) * flt(a.cop)

			gl_entries.append(
				prepare_gl(self, {"account": wh_account,
						 "debit": flt(amount),
						 "debit_in_account_currency": flt(amount),
						 "cost_center": self.cost_center,
						 "business_activity": self.business_activity
						})
				)

			gl_entries.append(
				prepare_gl(self, {"account": expense_account,
						 "credit": flt(amount),
						 "credit_in_account_currency": flt(amount),
						 "cost_center": self.cost_center,
						 "business_activity": self.business_activity
						})
				)

		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=True)


	def make_raw_material_stock_ledger(self):
		sl_entries = []

		for a in self.raw_materials:
			sl_entries.append(prepare_sl(self,
				{
					"stock_uom": a.uom,
					"item_code": a.item_code,
					"actual_qty": -1 * flt(a.qty),
					"warehouse": self.warehouse,
					"incoming_rate": 0
				}))

		if sl_entries: 
			if self.docstatus == 2:
				sl_entries.reverse()

			self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')

	def make_raw_material_gl_entry(self):
		gl_entries = []

		wh_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": self.warehouse}, "name")
		if not wh_account:
			frappe.throw(str(self.warehouse) + " is not linked to any account.")

		for a in self.raw_materials:
			stock_qty, map_rate = get_stock_balance(a.item_code, self.warehouse, self.posting_date, self.posting_time, with_valuation_rate=True)
                        amount = flt(a.qty) * flt(map_rate)

			expense_account = frappe.db.get_value("Item", a.item_code, "expense_account")
			if not expense_account:
				frappe.throw("Set Budget Account in Item Master")		

			gl_entries.append(
				prepare_gl(self, {"account": wh_account,
						 "credit": flt(amount),
						 "credit_in_account_currency": flt(amount),
						 "cost_center": self.cost_center,
						 "business_activity": self.business_activity
						})
				)

			gl_entries.append(
				prepare_gl(self, {"account": expense_account,
						 "debit": flt(amount),
						 "debit_in_account_currency": flt(amount),
						 "cost_center": self.cost_center,
						 "business_activity": self.business_activity
						})
				)

		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=True)

	def make_production_entry(self):
		for a in self.items:
			doc = frappe.new_doc("Production Entry")
			doc.flags.ignore_permissions = 1
			doc.item_code = a.item_code
			doc.item_name = a.item_name
			doc.qty = a.qty
			doc.uom = a.uom
			doc.cop = a.cop
			doc.company = self.company
			doc.currency = self.currency
			doc.business_activity = self.business_activity
			doc.branch = self.branch
			doc.location = self.location
			doc.cost_center = self.cost_center
			doc.warehouse = self.warehouse
			doc.posting_date = str(self.posting_date) + " " + str(self.posting_time)
			doc.ref_doc = self.name
			doc.submit()

	def delete_production_entry(self):
		frappe.db.sql("delete from `tabProduction Entry` where ref_doc = %s", self.name)




