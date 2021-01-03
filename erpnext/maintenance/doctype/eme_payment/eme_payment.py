# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.accounts.utils import get_tds_account
from erpnext.custom_utils import check_uncancelled_linked_doc, prepare_gl, check_future_date, check_budget_available

class EMEPayment(Document):
	def validate(self):
		self.validate_data()
		check_future_date(self.posting_date)
		self.check_remarks()
		self.calculate_totals()

	def validate_data(self):
		is_disabled = frappe.db.get_value("Branch", self.branch, "is_disabled")
		if is_disabled:
			frappe.throw("Cannot use a disabled branch in transaction")

	def check_remarks(self):
		if not self.remarks:
			self.remarks = "EME payment to {0}".format(self.supplier)
		if self.deduction_amount and not self.deduction_remarks:
			frappe.throw("Deduction Remarks is mandatory")

        def get_logbooks(self):
		if not self.branch:
			frappe.throw("Select Branch")
		if not self.supplier:
			frappe.throw("Select Supplier")

		if not self.from_date or not self.to_date:
			frappe.throw("From Date and To Date are mandatory")

		query = "select l.name as logbook, l.posting_date, l.equipment_hiring_form, li.expense_head, li.hours as total_hours, l.equipment from tabLogbook l, `tabLogbook Item` li where li.parent = l.name and l.docstatus = 1 and l.paid = 0 and l.supplier = %(supplier)s and l.branch = %(branch)s and l.posting_date between %(from_date)s and %(to_date)s order by l.posting_date, li.expense_head"
                entries = frappe.db.sql(query, {"supplier": self.supplier, "from_date": self.from_date, "to_date": self.to_date, "branch": self.branch}, as_dict=True)
                self.set('items', [])

		if len(entries) == 0:
			frappe.msgprint("No valid logbooks found!")

		total = 0
                for d in entries:
			d.rate = frappe.db.get_value("Equipment Hiring Form", d.equipment_hiring_form, "rate")
			d.amount = flt(d.total_hours * d.rate, 2)
			total += d.amount
                        row = self.append('items', {})
                        row.update(d)
		self.total_amount = total
		self.calculate_totals()

	def calculate_totals(self):
		settings = frappe.get_single("Accounts Settings")
		total = 0
		
		for a in self.items:
			total += a.amount
			doc = frappe.get_doc("Equipment", equipment)
			a.equipment_no = doc.equipment_number
		self.total_amount = total

		# tds
                if self.tds_percent:
                        self.tds_amount  = flt(self.total_amount) * flt(self.tds_percent) / 100.0
                        self.tds_account = get_tds_account(self.tds_percent)
                else:
                        self.tds_amount  = 0
                        self.tds_account = None

		if self.deduction_amount and not self.deduction_account:
			self.deduction_account = settings.eme_deduction_account
			if not self.deduction_account:
				frappe.throw("Set EME Deduction Account in Account Settings")

		self.payable_amount = flt(self.total_amount, 2) - flt(self.tds_amount, 2) - flt(self.deduction_amount, 2)

	def on_submit(self):
		self.validate_logbook()
		self.update_general_ledger()
		self.update_logbook()

	def on_cancel(self):
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		
		self.update_general_ledger()
		self.update_logbook()
		self.cancel_budget()

	def on_update_after_submit(self):
		if self.clearance_date:
			frappe.throw("Already done bank reconciliation.")
		if not self.cheque_no or not self.cheque_date:
			frappe.throw("Both Cheque No and Date are mandatory")

	def validate_logbook(self):
		for a in self.items:
			paid = frappe.db.get_value("Logbook", a.logbook, "paid")
			if paid == 1:
				frappe.throw("{0} has already been paid. Please get logbooks again".format(frappe.bold(frappe.get_desk_link("Logbook", a.logbook))))
			
	def update_general_ledger(self):
		gl_entries = []
		amount_data = self.get_segregated_amounts()
		
		for a in amount_data:
			creditor_account = frappe.db.get_value("Expense Head", a.expense_head, "expense_account")
			if not creditor_account:
				frappe.throw("Set Expense Account under Expense Head")

			if self.docstatus == 1:
				check_budget_available(self.cost_center, creditor_account, self.posting_date, a.amount)
				self.consume_budget(self.cost_center, creditor_account, a.amount)

			gl_entries.append(
				prepare_gl(self, {"account": creditor_account,
						 "debit": flt(a.amount),
						 "debit_in_account_currency": flt(a.amount),
						 "cost_center": self.cost_center,
						 "party_type": "Supplier",
						 "party": self.supplier,
						})
				)

		if self.tds_amount:
			gl_entries.append(
				prepare_gl(self, {"account": self.tds_account,
						 "credit": flt(self.tds_amount),
						 "credit_in_account_currency": flt(self.tds_amount),
						 "cost_center": self.cost_center,
						 "party_type": "Supplier",
						 "party": self.supplier,
						})
				)
	
		if self.deduction_amount:
			gl_entries.append(
				prepare_gl(self, {"account": self.deduction_account,
						 "credit": flt(self.deduction_amount),
						 "credit_in_account_currency": flt(self.deduction_amount),
						 "cost_center": self.cost_center,
						 "party_type": "Supplier",
						 "party": self.supplier,
						 "remarks": self.deduction_remarks
						})
				)
	
		
		gl_entries.append(
			prepare_gl(self, {"account": self.bank_account,
			 "credit": flt(self.payable_amount) ,
			 "credit_in_account_currency": flt(self.payable_amount) ,
			 "cost_center": self.cost_center,
			})
		)

		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)

	def get_segregated_amounts(self):
		return frappe.db.sql("select expense_head, sum(amount) as amount from `tabEME Payment Item` where parent = %(name)s group by expense_head", {"name": self.name}, as_dict=1)

	def update_logbook(self):
		for a in frappe.db.sql("select distinct logbook from `tabEME Payment Item` where parent = %(name)s", {"name": self.name}, as_dict=1):
			value = 1
			if self.docstatus == 2:
				value = 0
			logbook = frappe.get_doc("Logbook", a.logbook)
			logbook.db_set("paid", value)
	
	def cancel_budget(self):
		if self.docstatus == 2:
			frappe.db.sql("delete from `tabCommitted Budget` where po_no = %s", self.name)
			frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name)

        def consume_budget(self, cc, account, amount):
                bud_obj = frappe.get_doc({
                        "doctype": "Committed Budget",
                        "account": account,
                        "cost_center": cc,
                        "po_no": self.name,
                        "po_date": self.posting_date,
                        "amount": amount,
                        "item_code": None,
                        "poi_name": self.name,
                        "date": frappe.utils.nowdate(),
			"consumed" : 1
                        })
                bud_obj.flags.ignore_permissions = 1
                bud_obj.submit()

                consume = frappe.get_doc({
                        "doctype": "Consumed Budget",
                        "account": account,
                        "cost_center": cc,
                        "po_no": self.name,
                        "po_date": self.posting_date,
                        "amount": amount,
                        "pii_name": self.name,
                        "item_code": None,
                        "com_ref": bud_obj.name,
                        "date": frappe.utils.nowdate()})
                consume.flags.ignore_permissions=1
                consume.submit()




