# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate, nowtime, getdate
from erpnext.accounts.utils import get_fiscal_year
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, check_budget_available
from erpnext.controllers.stock_controller import StockController

class POL(StockController):
	def validate(self):
		check_future_date(self.posting_date)
		self.set_warehouse()
		self.validate_data()
		self.validate_posting_time()
		self.validate_uom_is_integer("stock_uom", "qty")
		self.validate_item()

	def set_warehouse(self):
		cc = get_branch_cc(self.equipment_branch)
		equipment_warehouse = frappe.db.get_value("Cost Center", cc, "warehouse")
		if not equipment_warehouse:
			frappe.throw("No Warehouse is linked with Cost Center <b>" + str(cc) + "</b>")
		self.equipment_warehouse = equipment_warehouse

	def validate_data(self):
		if not self.fuelbook_branch or not self.equipment_branch:
			frappe.throw("Fuelbook and Equipment Branch are mandatory")

		if flt(self.qty) <= 0 or flt(self.rate) <= 0:
			frappe.throw("Quantity and Rate should be greater than 0")

		if not self.warehouse:
			frappe.throw("Warehouse is Mandatory. Set the Warehouse in Cost Center")

		if not self.equipment_category:
			frappe.throw("Equipment Category Missing")

		if self.branch != self.fuelbook_branch:
			frappe.throw("Transaction Branch and Fuelbook Branch should be same")
	
		if self.book_type == "Own":
			if self.fuelbook != frappe.db.get_value("Equipment", self.equipment, "fuelbook"):
				frappe.throw("Fuelbook (<b>" + str(self.fuelbook) + "</b>) is not registered to <b>" + str(self.equipment) + "</b>")

	def validate_item(self):
		is_stock = frappe.db.get_value("Item", self.pol_type, "is_stock_item")
		if not is_stock:
			frappe.throw(str(self.item_name) + " is not a stock item")

	def on_submit(self):
		if getdate(self.posting_date) > getdate("2018-03-31"):
			self.update_stock_ledger()
		self.check_budget()
		self.update_general_ledger()

		if self.direct_consumption:
			self.consume_pol()

	def check_budget(self):
		cc = get_branch_cc(self.equipment_branch)
		account = frappe.db.get_value("Equipment Category", self.equipment_category, "budget_account")

		check_budget_available(cc, account, self.posting_date, self.total_amount)
		self.consume_budget(cc, account)

	##
	# Update the Committedd Budget for checking budget availability
	##
	def consume_budget(self, cc, account):
		bud_obj = frappe.get_doc({
			"doctype": "Committed Budget",
			"account": account,
			"cost_center": cc,
			"po_no": self.name,
			"po_date": self.posting_date,
			"amount": self.total_amount,
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
			"amount": self.total_amount,
			"pii_name": self.name,
			"item_code": self.pol_type,
			"com_ref": bud_obj.name,
			"date": frappe.utils.nowdate()})
		consume.flags.ignore_permissions=1
		consume.submit()

	def update_stock_ledger(self):
		sl_entries = []
		sl_entries.append(prepare_sl(self, 
				{
					"actual_qty": flt(self.qty), 
					"warehouse": self.equipment_warehouse, 
					"incoming_rate": round(flt(self.total_amount) / flt(self.qty) , 2)
				}))

		if self.direct_consumption:
			sl_entries.append(prepare_sl(self,
					{
						"actual_qty": -1 * flt(self.qty), 
						"warehouse": self.equipment_warehouse, 
						"incoming_rate": 0
					}))
 
		if self.docstatus == 2:
			sl_entries.reverse()

		self.make_sl_entries(sl_entries, self.amended_from and 'Yes' or 'No')

	def update_general_ledger(self):
		gl_entries = []
		
		creditor_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		if not creditor_account:
			frappe.throw("Set Default Payable Account in Company")

		expense_account = self.get_expense_account()

		cost_center = get_branch_cc(self.equipment_branch)

		gl_entries.append(
			prepare_gl(self, {"account": expense_account,
					 "debit": flt(self.total_amount),
					 "debit_in_account_currency": flt(self.total_amount),
					 "cost_center": cost_center,
					})
			)

		gl_entries.append(
			prepare_gl(self, {"account": creditor_account,
					 "credit": flt(self.total_amount),
					 "credit_in_account_currency": flt(self.total_amount),
					 "cost_center": self.cost_center,
					 "party_type": "Supplier",
					 "party": self.supplier,
					 "against_voucher": self.name,
                                         "against_voucher_type": self.doctype,
					})
			)

		if self.equipment_branch != self.fuelbook_branch:
			ic_account = frappe.db.get_single_value("Accounts Settings", "intra_company_account")
			if not ic_account:
				frappe.throw("Setup Intra-Company Account in Accounts Settings")

			customer_cc = get_branch_cc(self.equipment_branch)

			gl_entries.append(
				prepare_gl(self, {"account": ic_account,
						 "credit": flt(self.total_amount),
						 "credit_in_account_currency": flt(self.total_amount),
						 "cost_center": customer_cc,
						})
				)

			gl_entries.append(
				prepare_gl(self, {"account": ic_account,
						 "debit": flt(self.total_amount),
						 "debit_in_account_currency": flt(self.total_amount),
						 "cost_center": self.cost_center,
						})
				)

		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)

	def get_expense_account(self):
		if self.direct_consumption:
			expense_account = frappe.db.get_value("Equipment Category", self.equipment_category, "budget_account")
			if not expense_account:
				frappe.throw("Set Budget Account in Equipment Category")		
		else:
			expense_account = frappe.db.get_value("Account", {"account_type": "Stock", "warehouse": self.warehouse}, "name")
			if not expense_account:
				frappe.throw(str(self.warehouse) + " is not linked to any account.")
		return expense_account

	def on_cancel(self):
		if getdate(self.posting_date) > getdate("2018-03-31"):
			self.update_stock_ledger()
			self.update_general_ledger()
		docstatus = frappe.db.get_value("Journal Entry", self.jv, "docstatus")
		if docstatus and docstatus != 2:
			frappe.throw("Cancel the Journal Entry " + str(self.jv) + " and proceed.")

		self.db_set("jv", "")

		if self.direct_consumption:
			self.cancel_consumed_pol()
		self.cancel_budget_entry()

	def cancel_consumed_pol(self):
		frappe.db.sql("delete from `tabConsumed POL` where reference_type = 'POL' and reference_name = %s", (self.name))

	##
	# Cancel budget check entry
	##
	def cancel_budget_entry(self):
		frappe.db.sql("delete from `tabCommitted Budget` where po_no = %s", self.name)
		frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name)

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		veh_cat = frappe.db.get_value("Equipment", self.equipment, "equipment_category")
		if veh_cat:
			if veh_cat == "Pool Vehicle":
				pol_account = frappe.db.get_single_value("Maintenance Accounts Settings", "pool_vehicle_pol_expenses")
			else:
				pol_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_pol_expense_account")
		else:
			frappe.throw("Can not determine machine category")
		#expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		expense_bank_account = frappe.db.get_value("Company", frappe.defaults.get_user_default("Company"), "default_payable_account")
		if not expense_bank_account:
 			frappe.throw("No Default Payable Account set in Company")

		if expense_bank_account and pol_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "POL (" + self.pol_type + " for " + self.equipment_number + ")"
			je.voucher_type = 'Bank Entry'
			je.naming_series = 'Bank Payment Voucher'
			je.remark = 'Payment against : ' + self.name;
			je.posting_date = self.posting_date
			je.branch = self.branch

			je.append("accounts", {
					"account": pol_account,
					"cost_center": self.cost_center,
					"reference_type": "POL",
					"reference_name": self.name,
					"debit_in_account_currency": flt(self.total_amount),
					"debit": flt(self.total_amount),
				})

			je.append("accounts", {
					"account": expense_bank_account,
					"cost_center": self.cost_center,
					"party_type": "Supplier",
					"party": self.supplier,
					"credit_in_account_currency": flt(self.total_amount),
					"credit": flt(self.total_amount),
				})

			je.insert()
			self.db_set("jv", je.name)
		else:
			frappe.throw("Define POL expense account in Maintenance Setting or Expense Bank in Branch")
		
	def consume_pol(self):
		con = frappe.new_doc("Consumed POL")	
		con.equipment = self.equipment
		con.pol_type = self.pol_type
		con.branch = self.branch
		con.date = self.posting_date
		con.qty = self.qty
		con.reference_type = "POL"
		con.reference_name = self.name
		con.submit()


