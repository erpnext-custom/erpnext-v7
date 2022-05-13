# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.accounts.utils import get_tds_account
from erpnext.custom_utils import check_uncancelled_linked_doc, prepare_gl, check_future_date, check_budget_available
from frappe.model.mapper import get_mapped_doc

class EMEPayment(Document):
	def validate(self):
		self.validate_data()
		check_future_date(self.posting_date)
		if not self.arrear_eme_payment:
			self.check_remarks()
		else:
			self.update_rate_amount()
		self.calculate_totals()

	def validate_data(self):
		is_disabled = frappe.db.get_value("Branch", self.branch, "is_disabled")
		if is_disabled:
			frappe.throw("Cannot use a disabled branch in transaction")
	#Function to pay arrear base on change in rate
	def update_rate_amount(self):
		for a in self.get("items"):
			ehf = frappe.db.get_value("Logbook", a.logbook, "equipment_hiring_form")
			rate = frappe.db.sql("""select hiring_rate as rate from `tabEHF Rate` where parent = '{0}' and '{1}' between from_date and to_date and docstatus = 1""".format(ehf, a.posting_date) , as_dict = 1, debug = 1)
			if rate:
				a.new_rate = flt(rate[0].rate)
				a.rate   = flt(a.new_rate) - flt(a.prev_rate)
				a.amount = flt(a.rate)  * flt(a.total_hours)

	def check_remarks(self):
		if not self.remarks:
			self.remarks = "EME payment to {0}".format(self.supplier)
		# if self.deduction_amount and not self.deduction_remarks:
		# 	frappe.throw("Deduction Remarks is mandatory")

        def get_logbooks(self):
		if not self.branch:
			frappe.throw("Select Branch")
		if not self.supplier:
			frappe.throw("Select Supplier")

		if not self.from_date or not self.to_date:
			frappe.throw("From Date and To Date are mandatory")

		query = """ SELECT l.name as logbook, l.posting_date, l.equipment_hiring_form, li.expense_head, li.hours as total_hours, l.equipment 
					FROM tabLogbook l, `tabLogbook Item` li 
					WHERE li.parent = l.name 
					AND l.docstatus = 1 
					AND l.paid = 0 
					AND l.supplier = %(supplier)s 
					AND l.branch = %(branch)s 
					AND l.posting_date BETWEEN %(from_date)s and %(to_date)s 
					ORDER BY l.posting_date, li.expense_head
				"""
	
                entries = frappe.db.sql(query, {"supplier": self.supplier, "from_date": self.from_date, "to_date": self.to_date, "branch": self.branch}, as_dict=True)
                self.set('items', [])

		if len(entries) == 0:
			frappe.msgprint("No valid logbooks found!")

		total = 0
		exist_list = {}
                for d in entries:
			exist = frappe.db.sql(""" SELECT eme.name FROM `tabEME Payment` eme, `tabEME Payment Item` emi  
				WHERE emi.parent = eme.name AND emi.logbook = '{0}' """.format(d.logbook))
			if exist:
				exist_list.setdefault(exist[0], []).append(d.logbook)
			else:		
				#d.rate = frappe.db.get_value("Equipment Hiring Form", d.equipment_hiring_form, "rate")
				d.rate = self.get_rate(d.equipment_hiring_form, d.posting_date)
				d.amount = flt(d.total_hours * d.rate, 2)
				total += d.amount
				row = self.append('items', {})
				row.update(d)
		if exist_list:
			frappe.msgprint("<b> {0} </b> </br> {1}".format(exist_list.keys(), exist_list.values()), title= "LogBook already pulled in EME Payment")
		"""
			AND NOT EXISTS ( SELECT eme.name FROM `tabEME Payment` eme, `tabEME Payment Item` emi                         WHERE emi.parent = eme.name AND emi.logbook = l.name) 
		"""
		self.total_amount = total
		self.calculate_totals()


	def get_rate(self, ehf, posting_date):
		arrear_eme_payment = None
		if not arrear_eme_payment:
			rate = frappe.db.sql("""select hiring_rate as rate from `tabEHF Rate` where parent = '{0}' and '{1}' between from_date and to_date and docstatus = 1""".format(ehf, posting_date) , as_dict = 1, debug = 1)
			if rate:
				return rate[0].rate
			else:
				frappe.throw("No rates defined in Equipment Hiring Form <b>{}</b> for data <b>{}</b>".format(ehf, posting_date))
		'''
		else:
			return frappe.db.get_value("Equipment Hiring Form", ehf, "rate")
		'''
	def calculate_totals(self):
		settings = frappe.get_single("Accounts Settings")
		total = 0
		
		for a in self.items:
			total += flt(a.amount)
			doc = frappe.get_doc("Equipment", a.equipment)
			a.equipment_no = doc.equipment_number
			a.equipment_type = doc.equipment_type
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

		total_deductions = 0
		for d in self.get('deduct_items'):
			if 0 >= d.amount:
				frappe.throw("Deduction amount should be more than zero")
			if not d.account:
				frappe.throw("Account is mandatory for deductions")
			total_deductions += flt(d.amount, 2)
		self.deduction_amount = total_deductions
		self.payable_amount = flt(self.total_amount, 2) - flt(self.tds_amount, 2) - flt(self.deduction_amount, 2)

	def on_submit(self):
		self.validate_workflow()
		self.validate_logbook()
		self.update_general_ledger()
		self.update_logbook()

	def validate_workflow(self):
		if self.workflow_state == "Paid" and self.docstatus == 0:
			self.workflow_state = "Payment Pending"

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
			if paid == 1 and not self.arrear_eme_payment:
				frappe.throw("{0} has already been paid. Please get logbooks again".format(frappe.bold(frappe.get_desk_link("Logbook", a.logbook))))
			
	def update_general_ledger(self):
		gl_entries = []
		amount_data = self.get_segregated_amounts()
		
		for a in amount_data:
			#creditor_account = frappe.db.get_value("Expense Head", a.expense_head, "expense_account")
			if not a.creditor_account:
				frappe.throw("Set Expense Account under Expense Head")

			if self.docstatus == 1:
				check_budget_available(self.cost_center, a.creditor_account, self.posting_date, a.amount)
				self.consume_budget(self.cost_center, a.creditor_account, a.amount)
			
			party = party_type = None
			account_type = frappe.db.get_value("Account", a.creditor_account, "account_type") or ""
			if account_type in ["Receivable", "Payable"]:
				party = self.supplier
				party_type = "Supplier"

			gl_entries.append(
				prepare_gl(self, {"account": a.creditor_account,
						"debit": flt(a.amount),
						"debit_in_account_currency": flt(a.amount),
						"cost_center": self.cost_center,
						"party_type": party_type,
						"party": party,
						})
				)
				
		if self.tds_amount:
			gl_entries.append(
				prepare_gl(self, {"account": self.tds_account,
						 "credit": flt(self.tds_amount),
						 "credit_in_account_currency": flt(self.tds_amount),
						 "cost_center": self.cost_center,
						})
				)
		'''
		if self.deduction_amount:
			party = party_type = None
			account_type = frappe.db.get_value("Account", self.deduction_account, "account_type") or ""
			if account_type in ["Receivable", "Payable"]:
				party = self.supplier
				party_type = "Supplier"

			gl_entries.append(
				prepare_gl(self, {"account": self.deduction_account,
					"credit": flt(self.deduction_amount),
					"credit_in_account_currency": flt(self.deduction_amount),
					"cost_center": self.cost_center,
					"party_type": party,
					"party": party_type,
					"remarks": self.deduction_remarks
					})
				)
		'''
		
		for d in self.get('deduct_items'):
			party = party_type = None
			if d.account_type in ["Receivable", "Payable"]:
				party = self.supplier
				party_type = "Supplier"

			gl_entries.append(
				prepare_gl(self, {"account": d.account,
						 "credit": flt(d.amount),
						 "credit_in_account_currency": flt(d.amount),
						 "cost_center": self.cost_center,
						 "party_type": party_type,
						 "party": party,
						 "remarks": d.remarks
						})
				)
	
		payable_account = frappe.db.get_value("Company", self.company, "default_payable_account")
		
		party = party_type = None
		account_type = frappe.db.get_value("Account", payable_account, "account_type") or ""
		if account_type in ["Receivable", "Payable"]:
			party = self.supplier
			party_type = "Supplier"	

		if payable_account != self.bank_account:	
			gl_entries.append(
				prepare_gl(self, {"account": payable_account,
				 "credit": flt(self.payable_amount) ,
				 "credit_in_account_currency": flt(self.payable_amount) ,
				 "cost_center": self.cost_center,
				 "party_type": party_type,
				 "party": party,
				})
			)
			
			gl_entries.append(
				prepare_gl(self, {"account": payable_account,
				 "debit": flt(self.payable_amount) ,
				 "debit_in_account_currency": flt(self.payable_amount) ,
				 "cost_center": self.cost_center,
				 "party_type": party_type,
				 "party": party,
				})
			) 

		party = party_type = None
		account_type = frappe.db.get_value("Account", self.bank_account, "account_type") or ""
		if account_type in ["Receivable", "Payable"]:
			party = self.supplier
			party_type = "Supplier"	

		gl_entries.append(
			prepare_gl(self, {"account": self.bank_account,
			 "credit": flt(self.payable_amount) ,
			 "credit_in_account_currency": flt(self.payable_amount) ,
			 "cost_center": self.cost_center,
			 "party_type": party_type,
			 "party": party,
			})
		)

		from erpnext.accounts.general_ledger import make_gl_entries
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2), update_outstanding="No", merge_entries=False)

	def get_segregated_amounts(self):
		return frappe.db.sql("select e.expense_account as creditor_account, sum(a.amount) as amount from `tabEME Payment Item` a, `tabExpense Head` e where e.name = a.expense_head and a.parent = %(name)s group by e.expense_account", {"name": self.name}, as_dict=1)

		#return frappe.db.sql("select expense_head, sum(amount) as amount from `tabEME Payment Item` where parent = %(name)s group by expense_head", {"name": self.name}, as_dict=1)

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

def set_missing_values(source, target):
	target.run_method("set_missing_values")
	
@frappe.whitelist()
def make_arrear_payment(source_name, target_doc=None):
	def postprocess(source, target_doc):
		set_missing_values(source, target_doc)

	def update_item(obj, target, source_parent):
		target.rate = 0.00

	doclist = get_mapped_doc("EME Payment", source_name, 	{
		"EME Payment": {
			"doctype": "EME Payment",
			"field_map": {
				"naming_series": "naming_series",
			},
			"validation": {
				"docstatus": ["=", 1],
			}
		},
		"EME Payment Item": {
			"doctype": "EME Payment Item",
			"field_map": {
					"rate": "prev_rate"
				},
			"postprocess": update_item
		}
	}, target_doc, postprocess)

	return doclist
