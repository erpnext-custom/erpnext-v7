# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, cint
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.custom_utils import check_future_date, get_settings_value, check_uncancelled_linked_doc,\
		check_budget_available, get_branch_cc
from erpnext.accounts.doctype.transporter_rate.transporter_rate import get_transporter_rate
from erpnext.accounts.utils import get_tds_account 

class TransporterPayment(AccountsController):
	def validate(self):
		self.validate_dates()
		self.set_debit_account()
		self.calculate_total()
		self.calculate_on_save()

	def validate_dates(self):
		check_future_date(self.posting_date)
		if self.from_date > self.to_date:
			frappe.throw("From Date cannot be grater than To Date")
			
		if not self.remarks:
			self.remarks = "Payment for {0}".format(self.registration_no)
	
	def set_debit_account(self):
		e = frappe.db.get_value("Equipment", self.equipment, "equipment_category")
		self.debit_account = frappe.db.get_value("Equipment Category", e, "budget_account")
	
		if self.unloading_amount:
			self.unloading_account = get_settings_value("Production Account Settings", self.company, "default_unloading_account")
	def calculate_on_save(self):
		trip_no = 0
		total_transporter_amount = 0
		unloading_amount = 0
		for i in self.items:
			trip_no = trip_no + 1
			total_transporter_amount = total_transporter_amount + i.transportation_amount
			unloading_amount = unloading_amount + i.unloading_amount

		self.total_trip = trip_no
		self.transportation_amount = total_transporter_amount
		self.unloading_amount = unloading_amount
		self.gross_amount = total_transporter_amount + unloading_amount
	
		pol_amount = 0
		for j in self.pols:
			pol_amount = pol_amount + j.amount

		self.pol_amount = pol_amount
		self.net_payable = self.gross_amount - self.pol_amount

		total_other_deduction = 0

		if self.deductions:
			for k in self.deductions:
				total_other_deduction = total_other_deduction + k.amount			
		
		if total_other_deduction > 0:
			if self.tds_amount > 0:		
				self.other_deductions = total_other_deduction + self.tds_amount
			else:
				self.other_deductions= total_other_deduction
		elif self.tds_amount > 0:
			self.other_deductions = self.tds_amount
		else:
			pass

			
		self.amount_payable = self.net_payable - self.other_deductions
		

	def calculate_total(self):
                other_deductions = 0



		if self.tds_percent:
			self.tds_amount = flt(self.gross_amount) * flt(self.tds_percent) / 100.0
			self.tds_account = get_tds_account(self.tds_percent)
		else:
			self.tds_amount = None	
			self.tds_account = None

                ##### Ver 1.0.190312 Ends, Added by SHIV on 2019/03/12
                for d in self.get("deductions"):
                        if d.party_type == "Equipment" and not d.party:
                                d.party = self.equipment
                                
                        if d.account_type != "Payable" and d.account_type != "Receivable" and d.party:
                                frappe.throw(_("Row#{0} : Party is not allowed against Non-payable or Non-receivable accounts.").format(d.idx), title="Invalid Data")

                        if (d.account_type == "Payable" or d.account_type == "Receivable") and not d.party:
                                frappe.throw(_("Row#{0} : Party is mandatory").format(d.idx), title="Missing Data")
                                
                        other_deductions += flt(d.amount)
                self.other_deductions = flt(other_deductions)+flt(self.tds_amount)
                ##### Ver 1.0.190312 Ends
                
		self.net_payable = flt(self.gross_amount) - flt(self.pol_amount)
		# Following line commented and subsequent added by SHIV on 2019/03/12
		#self.amount_payable = flt(self.gross_amount) - flt(self.pol_amount) - flt(self.tds_amount) - flt(self.deduction_amount)
		self.amount_payable = flt(self.net_payable) - flt(self.other_deductions)			

	def get_payment_details(self):
		production = []
		'''
		# Commented by SHIV on 2019/09/12 upon request from Dorji
		query = "select b.name as reference_row, a.posting_date, 'Production' as reference_type, a.name as reference_name, b.item_code, b.item_name, a.warehouse as receiving_warehouse, b.qty, b.unloading_by, b.equipment from `tabProduction` a, `tabProduction Product Item` b where a.name = b.parent and a.docstatus = 1 and b.transport_payment_done = 0 and a.posting_date between %s and %s and b.equipment = %s"	
		production = frappe.db.sql(query, (self.from_date, self.to_date, self.equipment), as_dict=True)
		'''

		query = "select b.name as reference_row, a.posting_date, 'Stock Entry' as reference_type, a.name as reference_name, b.item_code, b.item_name, b.t_warehouse as receiving_warehouse, b.received_qty as qty, a.unloading_by, a.equipment from `tabStock Entry` a, `tabStock Entry Detail` b where a.name = b.parent and a.docstatus = 1 and a.transport_payment_done = 0 and a.purpose = 'Material Transfer' and a.posting_date between %s and %s and a.equipment = %s"
		stock_transfer = frappe.db.sql(query, (self.from_date, self.to_date, self.equipment), as_dict=True)
	
		query = "select b.name as reference_row, a.posting_date, 'Delivery Note' as reference_type, a.name as reference_name, b.item_code, b.item_name, a.customer as receiving_warehouse, b.qty as qty, '' as unloading_by, a.equipment from `tabDelivery Note` a, `tabDelivery Note Item` b where a.name = b.parent and a.docstatus = 1 and a.posting_date between %s and %s and a.equipment = %s and transport_payment_done = 0"
		delivery_note = frappe.db.sql(query, (self.from_date, self.to_date, self.equipment), as_dict = True)
		entries = production + stock_transfer+delivery_note
		if not entries:
			frappe.throw("No Transportation Detail(s) for Equipment <b>{0}</b>".format(self.equipment))

		self.set('items', [])
		self.set('pols', [])

		self.total_trip = len(entries)

		trans_amount = unload_amount = pol_amount = 0

		for d in entries:
			equipment_type = frappe.db.get_value("Equipment", d.equipment,"equipment_type")
			#doc = get_transporter_rate(d.receiving_warehouse, d.posting_date, equipment_type, d.item_code)[0]
			doc = get_transporter_rate(d.receiving_warehouse, d.posting_date, equipment_type, d.item_code)
			d.transporter_rate = doc['name']
			if cint(self.total_trip) > flt(doc['threshold_trip']):
				d.transportation_rate = flt(doc['higher_rate'])
			else:
				d.transportation_rate = flt(doc['lower_rate'])
			d.transportation_amount = round(flt(d.transportation_rate) * flt(d.qty), 2)
			d.unloading_rate = doc['unloading_rate']
			if d.unloading_by == "Transporter":
				d.unloading_amount = round(flt(d.unloading_rate) * flt(d.qty), 2)
			else:
				d.unloading_amount = 0
			
			d.total_amount = flt(d.unloading_amount) + flt(d.transportation_amount)

			row = self.append('items', {})
			row.update(d)
			
			trans_amount = trans_amount + flt(d.transportation_amount)
			unload_amount = unload_amount + flt(d.unloading_amount)

		#POL Details
		query = "select posting_date, name as pol, pol_type as item_code, item_name, qty, rate, total_amount as amount from tabPOL where docstatus = 1 and transport_payment_done = 0 and posting_date between %s and %s and equipment = %s"
		for a in frappe.db.sql(query, (self.from_date, self.to_date, self.equipment), as_dict=1):
			row = self.append('pols', {})
			row.update(a)
			pol_amount = pol_amount + flt(a.amount)
	
		self.transportation_amount = trans_amount
		self.unloading_amount = unload_amount
		self.gross_amount = trans_amount + unload_amount
		self.pol_amount = pol_amount
		self.calculate_total()

	def on_submit(self):
		self.check_paid()
		self.check_budget()
		self.make_gl_entry()
		self.mark_paid(1)

	def check_paid(self):
		for a in self.items:
			if a.reference_type == "Production":
				eq = frappe.db.get_value("Production Product Item", a.reference_name, "equipment")
				if eq != self.equipment:
					frappe.throw("Transportation Details are not for " + str(self.equipment))
				paid = frappe.db.get_value("Production Product Item", a.reference_row, "transport_payment_done")
				if paid:
					frappe.throw("Payment Already Done")
			elif a.reference_type == "Stock Entry":
				eq = frappe.db.get_value("Stock Entry", a.reference_name, "equipment")
				if eq != self.equipment:
					frappe.throw("Transportation Details are not for " + str(self.equipment))
				paid = frappe.db.get_value("Stock Entry", a.reference_name, "transport_payment_done")
				if paid:
					frappe.throw("Payment Already Done")
			elif a.reference_type == "Delivery Note":
                                eq = frappe.db.get_value("Delivery Note", a.reference_name, "equipment")
                                if eq != self.equipment:
                                        frappe.throw("Transportation Details are not for " + str(self.equipment))
                                paid = frappe.db.get_value("Delivery Note", a.reference_name, "transport_payment_done")
                                if paid:
                                        frappe.throw("Payment Already Done")

			else:
				pass

	def check_budget(self):
		if self.docstatus == 2:
			frappe.db.sql("delete from `tabCommitted Budget` where po_no = %s", self.name)
			frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name)
			return

		cc = get_branch_cc(self.branch)
		trans_amount = flt(self.transportation_amount) - flt(self.pol_amount)
		if trans_amount:
			check_budget_available(cc, self.debit_account, self.posting_date, trans_amount)
			self.consume_budget(cc, self.debit_account, trans_amount)

		if self.unloading_amount:
			check_budget_available(cc, self.unloading_account, self.posting_date, self.unloading_amount)
			self.consume_budget(cc, self.unloading_account, self.unloading_amount)
	
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
                        "amount": amount,
                        "pii_name": self.name,
                        "item_code": None,
                        "com_ref": bud_obj.name,
                        "date": frappe.utils.nowdate()})
                consume.flags.ignore_permissions=1
                consume.submit()


	def before_cancel(self):
		if self.clearance_date:
			frappe.throw("BRS Updated transactions cannot be cancelled.")

		check_uncancelled_linked_doc(self.doctype, self.name)

	def on_cancel(self):
		self.make_gl_entry()
		self.check_budget()
		self.mark_paid(0)

	def make_gl_entry(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		gl_entries = []

		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		if not cost_center:
			frappe.throw("{0} is not linked to any Cost Center".format(self.branch))
		
		
		account_type = frappe.db.get_value("Account", self.credit_account, "account_type")
		party = party_type = None
		if account_type == "Receivable" or account_type == "Payable":
			party = self.equipment
			party_type = "Equipment"

		if self.amount_payable:
			gl_entries.append(
				self.get_gl_dict({
				       "account": self.credit_account,
				       "credit": self.amount_payable,
				       "credit_in_account_currency": self.amount_payable,
				       "against_voucher": self.name,
				       "party_type": party_type,
				       "party": party,
				       "against_voucher_type": self.doctype,
				       "cost_center": cost_center,
				}, self.currency)
			)

		trans_amount = flt(self.transportation_amount) - flt(self.pol_amount)
		if trans_amount > 0:
			gl_entries.append(
				self.get_gl_dict({
				       "account":  self.debit_account,
				       "debit": trans_amount,
				       "debit_in_account_currency": trans_amount,
				       "against_voucher": self.name,
				       "against_voucher_type": self.doctype,
				       "cost_center": cost_center,
				}, self.currency)
			)

		if self.unloading_amount:
			gl_entries.append(
				self.get_gl_dict({
				       "account":  self.unloading_account,
				       "debit": self.unloading_amount,
				       "debit_in_account_currency": self.unloading_amount,
				       "against_voucher": self.name,
				       "against_voucher_type": self.doctype,
				       "cost_center": cost_center,
				}, self.currency)
			)

		if self.tds_amount:
			gl_entries.append(
				self.get_gl_dict({
				       "account":  self.tds_account,
				       "credit": self.tds_amount,
				       "credit_in_account_currency": self.tds_amount,
				       "against_voucher": self.name,
				       "against_voucher_type": self.doctype,
				       "cost_center": cost_center,
				}, self.currency)
			)

		##### Ver 1.0.190312 Begins, Following code replaced by subsequent by SHIV on 2019/03/12
		'''
		if self.deduction_amount:
			gl_entries.append(
                                self.get_gl_dict({
                                       "account":  self.gl_account,
                                       "credit": self.deduction_amount,
                                       "credit_in_account_currency": self.deduction_amount,
                                       "against_voucher": self.name,
                                       "against_voucher_type": self.doctype,
                                       "cost_center": cost_center,
                                }, self.currency)
                        )
		'''
		for d in self.get("deductions"):
                        if d.amount:
                                gl_entries.append(
                                        self.get_gl_dict({
                                               "account":  d.account,
                                               "credit": flt(d.amount),
                                               "credit_in_account_currency": flt(d.amount),
                                               "against_voucher": self.name,
                                               "against_voucher_type": self.doctype,
                                               "cost_center": cost_center,
                                               "party_type": d.party_type,
                                               "party": d.party
                                        }, self.currency)
                                )
		##### Ver 1.0.190312 Ends
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
		
	def mark_paid(self, submit=1):
		for a in self.items:
			if a.reference_type == "Production":
				frappe.db.sql("update `tabProduction Product Item` set transport_payment_done = %s where name = %s", (submit, a.reference_row))
			elif a.reference_type == "Stock Entry":
				frappe.db.sql("update `tabStock Entry` set transport_payment_done = %s where name = %s", (submit, a.reference_name))
			
			elif a.reference_type == "Delivery Note":
				frappe.db.sql("update `tabDelivery Note` set transport_payment_done = %s where name = %s", (submit, a.reference_name))
			
			else:
				pass

		for b in self.pols:
			frappe.db.sql("update tabPOL set transport_payment_done = %s where name = %s", (submit, b.pol))

	def on_update_after_submit(self):
		if not self.cheque_no or not self.cheque_date:
			frappe.throw("Both Cheque No and Date are mandatory")

