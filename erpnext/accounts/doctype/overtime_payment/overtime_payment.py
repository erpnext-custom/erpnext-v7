# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, get_datetime, get_url, nowdate, now_datetime, money_in_words
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController
from frappe.model.mapper import get_mapped_doc


class OvertimePayment(AccountsController):
	def validate(self):
		self.validate_details()
	
	def validate_details(self):
		if not self.bank_account:
			self.bank_account = frappe.db.get("Branch", self.branch, "expense_bank_account")
			if not self.bank_account:
				frappe.throw("Expense Bank account not configured for branch {}".format(self.branch))

		if not self.debit_account:
			self.debit_account = frappe.db.get_single_value("HR Accounts Setting", "overtime_account")

		total_amount = 0.00
		for a in self.item:
			total_amount += a.total_amount

		if self.total_amount != total_amount:
			self.total_amount = total_amount
			self.payable_amount = total_amount

	def on_submit(self):
		self.consume_budget()
		self.post_gl_entry()
		self.update_overtime_application()

	def on_cancel(self):
		self.post_gl_entry()
		self.cancel_budget_entry()
		self.update_overtime_application()

	##
	# Update the Committedd Budget for checking budget availability
	##
	def consume_budget(self):
		bud_obj = frappe.get_doc({
			"doctype": "Committed Budget",
			"account": self.debit_account,
			"cost_center": self.cost_center,
			"po_no": self.name,
			"po_date": self.posting_date,
			"amount": self.payable_amount,
			"poi_name": self.name,
			"date": frappe.utils.nowdate(),
			"consumed" : 1
		})
		bud_obj.flags.ignore_permissions = 1
		bud_obj.submit()

		consume = frappe.get_doc({
				"doctype": "Consumed Budget",
				"account": self.debit_account,
				"cost_center": self.cost_center,
				"po_no": self.name,
				"po_date": self.posting_date,
				"amount": self.payable_amount,
				"pii_name": self.name,
				"com_ref": bud_obj.name,
				"date": frappe.utils.nowdate()})
		consume.flags.ignore_permissions=1
		consume.submit()

	##
	# Cancel budget check entry
	##
	def cancel_budget_entry(self):
		frappe.db.sql("delete from `tabCommitted Budget` where po_no = %s", self.name)
		frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name)
					
	def post_gl_entry(self):
		gl_entries = []
		gl_entries.append(
			self.get_gl_dict({
				"account": self.debit_account,
				"debit": self.payable_amount,
				"debit_in_account_currency": self.payable_amount,
				"voucher_no": self.name,
				"voucher_type": self.doctype,
				"cost_center": self.cost_center,
				"company": self.company,
				"remarks": "Overtime Payment",
				})
			)			
		gl_entries.append(
			self.get_gl_dict({
				"account": self.bank_account,
				"credit": self.payable_amount,
				"credit_in_account_currency": self.payable_amount,
				"voucher_no": self.name,
				"voucher_type": self.doctype,
				"cost_center": self.cost_center,
				"company": self.company,
				"remarks": "Overtime Payment",
				})
			)
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)

	def update_overtime_application(self):
		if self.docstatus == 1:
			for a in self.item:
				frappe.db.sql("update `tabOvertime Application` set overtime_payment = '{}' where name = '{}'".format(self.name, a.reference))
		else:
			frappe.db.sql("update `tabOvertime Application` set overtime_payment = '' where overtime_payment = '{}'".format(self.name))

	def get_ot_application(self):
		return frappe.db.sql("""
					select a.employee, a.employee_name, a.rate, a.total_hours, a.total_amount, a.name as reference
					from `tabOvertime Application` a
					where a.docstatus = 1 
					and a.posting_date between '{0}' and '{1}'
					and a.branch = '{2}'
					and (a.payment_jv is NULL or a.payment_jv = "")
					and NOT EXISTS(
						select 1 
						from `tabOvertime Payment` p, `tabOvertime Payment Item` i
						where p.name = i.parent
						and i.reference = a.name
						and p.docstatus = 1
					)
				""".format(self.from_date, self.to_date, self.branch), as_dict=True)


# ePayment Begins
@frappe.whitelist()
def make_bank_payment(source_name, target_doc=None):
    def set_missing_values(obj, target, source_parent):
        target.payment_type = None
        target.transaction_type = "Overtime Payment"
        target.posting_date = get_datetime()
        target.from_date = None
        target.to_date = None
        # bank_name, bank_branch, bank_account_no = frappe.db.get_value("Account", obj.credit_account, ['bank_name', 'bank_branch', 'bank_account_no'])
        # target.bank_name = bank_name
        # target.bank_branch = bank_branch
        # target.bank_account_no = bank_account_no

    doc = get_mapped_doc("Overtime Payment", source_name, {
            "Overtime Payment": {
                "doctype": "Bank Payment",
                "field_map": {
                    "name": "transaction_no",
                    #"credit_account": "paid_from",
                },
                "postprocess": set_missing_values,
            },
    }, target_doc, ignore_permissions=True)
    return doc
# ePayment Ends