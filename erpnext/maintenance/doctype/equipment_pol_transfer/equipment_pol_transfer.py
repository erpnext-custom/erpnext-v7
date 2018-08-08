# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.accounts.utils import get_fiscal_year
from frappe.utils import flt, getdate, nowdate
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, check_budget_available
from erpnext.stock.stock_ledger import get_valuation_rate

class EquipmentPOLTransfer(Document):
	def validate(self):
		check_future_date(self.posting_date)
		if flt(self.qty) < 1:
			frappe.throw("Quantity cannot be less than 1")

	def on_submit(self):
		self.adjust_consumed_pol()
		if self.from_branch != self.to_branch and getdate(self.posting_date) > getdate("2018-03-31"):
			self.check_budget()
			self.update_gl_entry()

	def check_budget(self):
		cc = get_branch_cc(self.to_branch)
		from_cc = get_branch_cc(self.from_branch)
		account = frappe.db.get_value("Equipment Category", frappe.db.get_value("Equipment", self.to_equipment, "equipment_category"), "budget_account")
		if not account:
			frappe.throw("Setup Budget Account in Equipment Category")
		valuation_rate = get_valuation_rate(self.pol_type, frappe.db.get_value("Cost Center", from_cc, "warehouse"))
		if not valuation_rate:
			frappe.throw("Valuation Rate could not be calculated. Check Cost Center and Warehouse Linkage")

		check_budget_available(cc, account, self.posting_date, valuation_rate)
		self.consume_budget(cc, account, valuation_rate)

	##
	# Update the Committedd Budget for checking budget availability
	##
	def consume_budget(self, cc, account, valuation_rate):
		bud_obj = frappe.get_doc({
			"doctype": "Committed Budget",
			"account": account,
			"cost_center": cc,
			"po_no": self.name,
			"po_date": self.posting_date,
			"amount": valuation_rate,
			"item_code": self.pol_type,
			"poi_name": self.name,
			"date": frappe.utils.nowdate()
			})
		bud_obj.flags.ignore_permissions = 1
		bud_obj.submit()

		consume = frappe.get_doc({
			"doctype": "Consumed Budget",
			"account": account,
			"cost_center": cc,
			"po_no": self.name,
			"po_date": self.posting_date,
			"amount": valuation_rate,
			"pii_name": self.name,
			"item_code": self.pol_type,
			"com_ref": bud_obj.name,
			"date": frappe.utils.nowdate()})
		consume.flags.ignore_permissions=1
		consume.submit()

	def update_gl_entry(self):
		gl_entries = []
		from_cc = get_branch_cc(self.from_branch)
		to_cc = get_branch_cc(self.to_branch)
		from_account = frappe.db.get_value("Equipment Category", frappe.db.get_value("Equipment", self.from_equipment, "equipment_category"), "budget_account")
		to_account = frappe.db.get_value("Equipment Category", frappe.db.get_value("Equipment", self.to_equipment, "equipment_category"), "budget_account")
		if not from_account and not to_account:
			frappe.throw("Check Budget Accounts Settings in Equipment Category")

		ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
		if not ic_account:
			frappe.throw("Setup Intra-Company Account in Accounts Settings")
		
		from erpnext.stock.stock_ledger import get_valuation_rate
		valuation_rate = get_valuation_rate(self.pol_type, frappe.db.get_value("Cost Center", from_cc, "warehouse"))
		if not valuation_rate:
			frappe.throw("Valuation Rate could not be calculated. Check Cost Center and Warehouse Linkage")

		gl_entries.append(
			prepare_gl(self, {"account": from_account,
					 "credit": flt(valuation_rate),
					 "credit_in_account_currency": flt(valuation_rate),
					 "cost_center": from_cc,
					})
			)

		gl_entries.append(
			prepare_gl(self, {"account": to_account,
					 "debit": flt(valuation_rate),
					 "debit_in_account_currency": flt(valuation_rate),
					 "cost_center": to_cc,
					})
			)

		gl_entries.append(
			prepare_gl(self, {"account": ic_account,
					 "debit": flt(valuation_rate),
					 "debit_in_account_currency": flt(valuation_rate),
					 "cost_center": from_cc,
					})
			)

		gl_entries.append(
			prepare_gl(self, {"account": ic_account,
					 "credit": flt(valuation_rate),
					 "credit_in_account_currency": flt(valuation_rate),
					 "cost_center": to_cc,
					})
			)

		if gl_entries:
			from erpnext.accounts.general_ledger import make_gl_entries
			make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=True)

	def on_cancel(self):
		if self.from_branch != self.to_branch and getdate(self.posting_date) > getdate("2018-03-31"):
			self.cancel_budget_entry()
			self.update_gl_entry()
		frappe.db.sql("delete from `tabPOL Entry` where reference_name = %s", (self.name))

	##
	# Cancel budget check entry
	##
	def cancel_budget_entry(self):
		frappe.db.sql("delete from `tabCommitted Budget` where po_no = %s", self.name)
		frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name)
	
	def adjust_consumed_pol(self):
		if getdate(self.posting_date) <= getdate("2018-03-31"):
                        return
		if self.from_branch == self.to_branch:
			own = 1
		else:
			own = 0
		if self.from_equipment and self.to_equipment:
			con = frappe.new_doc("POL Entry")	
			con.flags.ignore_permissions = 1
			con.equipment = self.from_equipment
			con.branch = self.from_branch
			con.pol_type = self.pol_type
			con.date = self.posting_date
			con.posting_time = self.posting_time
			con.qty = -1 * flt(self.qty)
			con.reference_type = "Equipment POL Transfer"
			con.reference_name = self.name
			con.type = "Receive"
			con.is_opening = 0
			con.own_cost_center = own
			con.submit()

			to = frappe.new_doc("POL Entry")	
			to.flags.ignore_permissions = 1
			to.equipment = self.to_equipment
			to.branch = self.to_branch
			to.is_opening = 0
			to.pol_type = self.pol_type
			to.date = self.posting_date
			to.posting_time = self.posting_time
			to.qty = self.qty
			to.reference_type = "Equipment POL Transfer"
			to.reference_name = self.name
			to.type = "Receive"
			to.own_cost_center = own
			to.submit()
		else:
			frappe.throw("Should have both 'From' and 'To' Equipment")



