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
import operator, math

class TransporterPayment(AccountsController):
	def validate(self):
		self.validate_dates()
		self.calculate_total()
		self.validate_defaults()

	def on_submit(self):
		self.check_paid()
		self.check_budget()
		self.make_gl_entry()
		self.mark_paid(1)

	def before_cancel(self):
		if self.clearance_date:
			frappe.throw("BRS Updated transactions cannot be cancelled.")

		check_uncancelled_linked_doc(self.doctype, self.name)

	def on_cancel(self):
		self.make_gl_entry()
		self.check_budget()
		self.mark_paid(0)

	def on_update_after_submit(self):
		if not self.cheque_no or not self.cheque_date:
			frappe.throw("Both Cheque No and Date are mandatory")

	def validate_defaults(self):
		if not self.get("items"):
			frappe.throw("No Transportation Detail(s) for Equipment <b>{0} </b> ".format(self.equipment))

		if not flt(self.gross_amount):
			frappe.throw(_("Gross Amount cannot be empty"))

	def validate_dates(self):
		check_future_date(self.posting_date)
		if self.from_date > self.to_date:
			frappe.throw("From Date cannot be grater than To Date")
			
		if not self.remarks:
			self.remarks = "Payment for {0}".format(self.registration_no)
	
	def calculate_total(self):
		settings = frappe.get_single("Accounts Settings")

		# transfer and delivery charges
		transfer_charges = 0
		delivery_charges = 0
		total_transporter_amount = 0
		unloading_amount = 0
		trip_log_charges = 0
		within_trip_count = 0
		production_transport_charges = 0
		production_trip_count = 0
		for i in self.items:
			if i.reference_type == 'Stock Entry':
				transfer_charges += flt(i.transportation_amount)

			if i.reference_type == 'Delivery Note':
				delivery_charges += flt(i.transportation_amount)

			if i.reference_type == 'Transporter Trip Log':
				trip_log_charges += flt(i.transportation_amount)
				within_trip_count += 1

			if i.reference_type == 'Production':
				production_transport_charges += flt(i.transportation_amount)
				production_trip_count += 1
				
			total_transporter_amount += flt(i.transportation_amount)
			unloading_amount += flt(i.unloading_amount)
			
		self.transfer_charges 	= flt(transfer_charges)
		self.delivery_charges  	= flt(delivery_charges)
		self.transportation_amount = flt(total_transporter_amount)
		self.within_warehouse_trip = within_trip_count
		self.production_trip_count = production_trip_count
		self.within_warehouse_amount = flt(trip_log_charges)
		self.unloading_amount 	= flt(unloading_amount)
		self.production_transport_amount = flt(production_transport_charges)
		self.gross_amount 	= flt(self.transportation_amount) + flt(self.unloading_amount)

		# pol
		pol_amount = 0
		for j in self.pols:
			if not flt(j.allocated_amount):
				j.allocated_amount = flt(j.amount)
			pol_amount += flt(j.allocated_amount)

		self.pol_amount  	= flt(pol_amount)
		self.net_payable 	= flt(self.gross_amount) - flt(self.pol_amount)

		# unloading
		if self.unloading_amount:
			self.unloading_account = get_settings_value("Production Account Settings", self.company, "default_unloading_account")
			if not self.unloading_account:
				frappe.throw(_("GL for {} is not set under {}")\
					.format(frappe.bold("Default Unloading Account"), frappe.bold("Production Account Settings")))

		# security deposit
		if self.security_deposit_percent:
			self.security_deposit_amount = flt(self.gross_amount) * flt(self.security_deposit_percent) / 100.0
                        self.security_deposit_account = settings.security_deposit_account 
			if not self.security_deposit_account:
				frappe.throw(_("GL for {} is not set under {}")\
					.format(frappe.bold("Security Deposit Received"), frappe.bold("Accounts Settings")))
		else:
			self.security_deposit_amount = 0
			self.security_deposit_account= None
			
		# tds
		if self.tds_percent:
			self.tds_amount  = flt(self.gross_amount) * flt(self.tds_percent) / 100.0
			self.tds_account = get_tds_account(self.tds_percent)
		else:
			self.tds_amount  = 0
			self.tds_account = None

		# weighbridge
		self.total_trip = len(self.get("items"))
		if self.weighbridge_charge:
			self.weighbridge_amount  = flt(self.total_trip) * flt(self.weighbridge_charge)
			self.weighbridge_account = settings.weighbridge_account
			if not self.weighbridge_account:
				frappe.throw(_("GL for {} is not set under {}")\
					.format(frappe.bold("Income from Weighbridge Account"), frappe.bold("Accounts Settings")))
		else:
			self.weighbridge_amount  = 0
			self.weighbridge_account = None

		# other deductions
                other_deductions = 0
                for d in self.get("deductions"):
                        if d.party_type == "Equipment" and not d.party:
                                d.party = self.equipment
                                
                        if d.account_type != "Payable" and d.account_type != "Receivable" and d.party:
                                frappe.throw(_("Row#{0} : Party is not allowed against Non-payable or Non-receivable accounts.").format(d.idx), title="Invalid Data")

                        if (d.account_type == "Payable" or d.account_type == "Receivable") and not d.party:
                                frappe.throw(_("Row#{0} : Party is mandatory").format(d.idx), title="Missing Data")
                                
                        other_deductions += flt(d.amount)

                self.other_deductions 	= flt(other_deductions) + flt(self.tds_amount) + flt(self.security_deposit_amount)
		self.amount_payable 	= flt(self.net_payable) - flt(self.weighbridge_amount) - flt(self.other_deductions)			

	def get_stock_entries(self, cost_center):
		return frappe.db.sql("""select b.name as reference_row, a.posting_date, 
					'Stock Entry' as reference_type, a.name as reference_name, 
					b.item_code, b.item_name, 
					b.s_warehouse as from_warehouse, b.t_warehouse as receiving_warehouse, 
					b.received_qty as qty, a.unloading_by, a.equipment 
				from `tabStock Entry` a, `tabStock Entry Detail` b 
				where a.docstatus = 1 
				and a.transport_payment_done = 0 
				and a.purpose = 'Material Transfer' 
				and a.posting_date between "{0}" and "{1}" 
				and a.equipment = "{2}"
				and b.parent = a.name
				and b.cost_center = "{3}"
				""".format(self.from_date, self.to_date, self.equipment, cost_center), as_dict = True)

	def get_delivery_notes(self, cost_center):
		return frappe.db.sql("""select b.name as reference_row, a.posting_date, 
					'Delivery Note' as reference_type, a.name as reference_name, 
					b.item_code, b.item_name, 
					b.warehouse as from_warehouse, a.customer as receiving_warehouse, 
					b.qty as qty, '' as unloading_by, a.equipment 
				from `tabDelivery Note` a, `tabDelivery Note Item` b 
				where a.docstatus = 1 
				and a.posting_date between "{0}" and "{1}" 
				and a.equipment = "{2}" 
				and a.transport_payment_done = 0
				and b.parent = a.name
				and b.cost_center = "{3}"
				""".format(self.from_date, self.to_date, self.equipment, cost_center), as_dict = True)

	def get_transporter_trip_log(self, cost_center):
		return frappe.db.sql("""select b.name as reference_row, a.posting_date, 
					'Transporter Trip Log' as reference_type, a.name as reference_name, 
					b.item as item_code, b.item_name, b.amount as transportation_amount,
					a.warehouse as from_warehouse, a.warehouse as receiving_warehouse, 
					b.qty as qty, b.equipment, b.transporter_rate, b.rate as transportation_rate, b.expense_account
				from `tabTransporter Trip Log` a, `tabTrip Log Item` b
				where a.name = b.parent 
				and a.docstatus = 1 
				and a.posting_date between "{0}" and "{1}" 
				and b.equipment = "{2}"
				and a.cost_center = "{3}"
				and b.transport_payment_done = 0
				""".format(self.from_date, self.to_date, self.equipment, cost_center), as_dict = True)

	#production Transporter Based on Transporter Rate Base on
	def get_production_transportation(self, rate_base_on):
		return frappe.db.sql("""select b.name as reference_row, a.posting_date, 'Production' as reference_type, 
					a.name as reference_name, b.item_code, b.item_name, b.rate as transportation_rate, 
					b.amount as transportation_amount, b.qty, b.unloading_by, b.equipment, a.warehouse as from_warehouse, 
					if(a.transfer = 1, a.to_warehouse, a.warehouse) as receiving_warehouse, b.equipment,
					b.transporter_rate as transporter_rate, b.transportation_expense_account as expense_account
				from `tabProduction` a, `tabProduction Product Item` b
				where a.name = b.parent and a.docstatus = 1 
				and a.posting_date between "{0}" and "{1}" 
				and b.equipment = "{2}"
				and a.branch = '{3}'
				and b.transporter_payment_eligible = 1
				and b.transport_payment_done = 0
				and a.transporter_rate_base_on = '{4}'
				""".format(self.from_date, self.to_date, self.equipment, self.branch, rate_base_on), as_dict = True)

	def get_payment_details(self):
		self.set('items', [])
		self.set('pols', [])

		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		if not cost_center:
			frappe.throw("Branch {0} is not linked to any Cost Center".format(frappe.get_desk_link("Branch", self.branch)))
		
		# get stock entries
		stock_transfer = self.get_stock_entries(cost_center) 
	
		# get delivery notes
		delivery_note  = self.get_delivery_notes(cost_center) 

		# get Trips within warehouse
		within_warehouse_trips = self.get_transporter_trip_log(cost_center)

		# get Trips from production location based
		production_location = self.get_production_transportation("Location")

		# get Trips from production warehouse based
		production_warehouse = self.get_production_transportation("Warehouse")
		
		entries = production_warehouse + stock_transfer + delivery_note
		if not entries and not within_warehouse_trips and not production_location:
			frappe.throw("No Transportation Detail(s) for Equipment <b>{0} </b> ".format(self.equipment))

		self.total_trip = len(entries)
		trans_amount    = unload_amount = pol_amount = 0

		# populate items
		for d in entries:
			equipment_type = frappe.db.get_value("Equipment", d.equipment,"equipment_type")
			tr = get_transporter_rate(d.from_warehouse, d.receiving_warehouse, d.posting_date, equipment_type, d.item_code)

			d.transporter_rate = tr.name
			if cint(self.total_trip) > flt(tr.threshold_trip):
				d.transportation_rate = flt(tr.higher_rate)
			else:
				d.transportation_rate = flt(tr.lower_rate)

			d.unloading_rate  = tr.unloading_rate
			if d.unloading_by == "Transporter":
				d.unloading_amount = round(flt(d.unloading_rate) * flt(d.qty), 2)
			else:
				d.unloading_amount = 0
			
			d.expense_account 	= tr.expense_account
			d.transportation_amount = round(flt(d.transportation_rate) * flt(d.qty), 2)
			d.total_amount 		= flt(d.unloading_amount) + flt(d.transportation_amount)
			trans_amount 		+= flt(d.transportation_amount)
			unload_amount 		+= flt(d.unloading_amount)

			row = self.append('items', {})
			row.update(d)

		# populate items from Transporter Trips Log
		for d in within_warehouse_trips:
			d.total_amount 		= flt(d.transportation_amount)
			trans_amount 		+= flt(d.transportation_amount)
			row = self.append('items', {})
			row.update(d)

		# populate items from Production 
		for d in production_location:
			d.total_amount 	= flt(d.transportation_amount)
			trans_amount 	+= flt(d.transportation_amount)
			row = self.append('items', {})
			row.update(d)
	
		#POL Details
		query = """select posting_date, name as pol, pol_type as item_code, 
				item_name, qty, rate, total_amount as amount, 
				total_amount as allocated_amount,
				fuelbook_branch 
			from `tabPOL` 
			where cost_center = %s 
			and docstatus = 1 
			and transport_payment_done = 0 
			and posting_date between %s and %s and equipment = %s"""
		for a in frappe.db.sql(query, (cost_center, self.from_date, self.to_date, self.equipment), as_dict=1):
			row = self.append('pols', {})
			row.update(a)
	
		self.calculate_total()
		return flt(self.amount_payable)

	def check_paid(self):
		for a in self.items:
			if a.reference_type == "Production":
				eq = frappe.db.get_value("Production Product Item", a.reference_row, "equipment")
				if eq != self.equipment:
					frappe.throw("Transportation Details are not for " + str(self.equipment))
				paid = frappe.db.get_value("Production Product Item", a.reference_row, "transport_payment_done")
				if paid:
					frappe.throw("Payment Already Done")
			elif a.reference_type == "Stock Entry":
				eq = frappe.db.get_value("Stock Entry", a.reference_name, "equipment")
				if eq != self.equipment:
					frappe.throw(_("Transportation Details are not for {} under Stock Entry {}")\
						.format(frappe.get_desk_link('Equipment',self.equipment), frappe.get_desk_link('Stock Entry', a.reference_name)))
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
			elif a.reference_type == 'Transporter Trip Log':
				eq = frappe.db.get_value("Trip Log Item", a.reference_row, "equipment")
				if eq != self.equipment:
						frappe.throw("Transportation Details are not for " + str(self.equipment))
				paid = frappe.db.get_value("Trip Log Item", a.reference_row, "transport_payment_done")
				if paid:
						frappe.throw("Payment Already Done")
			else:
				pass

	def return_wh(self):
		pass
		'''con = ''
		if self.item_code = '500075':
			cond = ""
		if self.item_code = '300021':
			con = "from_warehouse = 'Dzongthong Warehouse Plant 1 - SMCL' and to_warehouse = 'Dzungdi Warehouse Plant 2 - SMCL'"	

		if self.item_code = ''
		'''

	def check_budget(self):
		if self.docstatus == 2:
			frappe.db.sql("delete from `tabCommitted Budget` where po_no = %s", self.name)
			frappe.db.sql("delete from `tabConsumed Budget` where po_no = %s", self.name)
			return

		cc = get_branch_cc(self.branch)
		trans_amount = flt(self.transportation_amount) - flt(self.pol_amount)
		if (flt(self.transfer_charges) +  flt(self.delivery_charges)) > 0:
			items = self.get_expense_gl()

			for k,v in items.iteritems():
				check_budget_available(cc, k, self.posting_date, v)
				self.consume_budget(cc, k, v)
	
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

        def get_expense_gl(self):
                items = {}
                total_transportation_amount = 0
		for i in self.get("items"): 
			if str(i.expense_account) in items:
				items[str(i.expense_account)] = flt(items[str(i.expense_account)]) + flt(i.transportation_amount)
			else:
				items.setdefault(str(i.expense_account),flt(i.transportation_amount))
			total_transportation_amount += flt(i.transportation_amount)

                # pro-rate POL expenses against each expense GL
                if flt(total_transportation_amount) and flt(self.pol_amount):
                        deduct_pct  = 0
                        deduct_amt  = 0
                        balance_amt = flt(self.pol_amount)
                        counter     = 0
                        for k,v in sorted(items.items(), key=operator.itemgetter(1)):
                                counter += 1
                                if counter == len(items):
                                        deduct_amt = balance_amt
                                else:
                                        deduct_pct = floor((flt(v)/flt(total_transportation_amount))*0.01)
                                        deduct_amt = floor(flt(self.pol_amount)*deduct_pct*0.01)
                                        balance_amt= balance_amt - deduct_amt

                                items[k] -= flt(deduct_amt)
                return items

	def make_gl_entry(self):
		from erpnext.accounts.general_ledger import make_gl_entries
		gl_entries = []

		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		if not cost_center:
			frappe.throw("{0} is not linked to any Cost Center".format(self.branch))
		
		
		party = party_type = None
		# amount_payable - CR
		if flt(self.amount_payable):
			party = party_type = None
			account_type = frappe.db.get_value("Account", self.credit_account, "account_type")
			if account_type == "Receivable" or account_type == "Payable":
				party = self.equipment
				party_type = "Equipment"

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

                # transportaion_amount - DR
		if (flt(self.transfer_charges) +  flt(self.delivery_charges)) + flt(self.within_warehouse_amount) + flt(self.production_transport_amount) > 0:
			items = self.get_expense_gl()
                        
			for k,v in items.iteritems():
				party = party_type = None
				account_type = frappe.db.get_value("Account", k, "account_type")
				if account_type == "Receivable" or account_type == "Payable":
					party = self.equipment
					party_type = "Equipment"

                                gl_entries.append(
                                        self.get_gl_dict({
                                                "account":  k,
                                                "debit": flt(v),
                                                "debit_in_account_currency": flt(v),
                                                "against_voucher": self.name,
                                                "against_voucher_type": self.doctype,
					        "party_type": party_type,
					        "party": party,
                                                "cost_center": cost_center,
                                        }, self.currency)
                                )

                # unloading_amount - DR
		if flt(self.unloading_amount):
			party = party_type = None
			account_type = frappe.db.get_value("Account", self.unloading_account, "account_type")
			if account_type == "Receivable" or account_type == "Payable":
				party = self.equipment
				party_type = "Equipment"

			gl_entries.append(
				self.get_gl_dict({
				       "account":  self.unloading_account,
				       "debit": self.unloading_amount,
				       "debit_in_account_currency": self.unloading_amount,
				       "against_voucher": self.name,
				       "against_voucher_type": self.doctype,
					"party_type": party_type,
					"party": party,
				       "cost_center": cost_center,
				}, self.currency)
			)

                # tds_amount - CR
		if flt(self.tds_amount):
			party = party_type = None
			account_type = frappe.db.get_value("Account", self.tds_account, "account_type")
			if account_type == "Receivable" or account_type == "Payable":
				party = self.equipment
				party_type = "Equipment"

			gl_entries.append(
				self.get_gl_dict({
				       "account":  self.tds_account,
				       "credit": self.tds_amount,
				       "credit_in_account_currency": self.tds_amount,
				       "against_voucher": self.name,
				       "against_voucher_type": self.doctype,
				       "party_type": party_type,
				       "party": party,
				       "cost_center": cost_center,
				}, self.currency)
			)

                # security_deposit_amount - CR
		if flt(self.security_deposit_amount):
			party = party_type = None
			account_type = frappe.db.get_value("Account", self.security_deposit_account, "account_type")
			if account_type == "Receivable" or account_type == "Payable":
				party = self.equipment
				party_type = "Equipment"

			gl_entries.append(
				self.get_gl_dict({
				       "account":  self.security_deposit_account,
				       "credit": self.security_deposit_amount,
				       "credit_in_account_currency": self.security_deposit_amount,
				       "against_voucher": self.name,
				       "against_voucher_type": self.doctype,
				       "party_type": party_type,
				       "party": party,
				       "cost_center": cost_center,
				}, self.currency)
			)

                # weighbridge amount - CR
		if flt(self.weighbridge_amount):
			party = party_type = None
			account_type = frappe.db.get_value("Account", self.weighbridge_account, "account_type")
			if account_type == "Receivable" or account_type == "Payable":
				party = self.equipment
				party_type = "Equipment"

			gl_entries.append(
				self.get_gl_dict({
				       "account":  self.weighbridge_account,
				       "credit": self.weighbridge_amount,
				       "credit_in_account_currency": self.weighbridge_amount,
				       "against_voucher": self.name,
				       "against_voucher_type": self.doctype,
				       "party_type": party_type,
				       "party": party,
				       "cost_center": cost_center,
				}, self.currency)
			)

                # deductions - CR
		for d in self.get("deductions"):
			party = party_type = None
			account_type = frappe.db.get_value("Account", d.account, "account_type")
			if account_type == "Receivable" or account_type == "Payable":
				party = self.equipment
				party_type = "Equipment"

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
		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
		
	def mark_paid(self, submit=1):
		for a in self.items:
			if a.reference_type == "Production":
				frappe.db.sql("update `tabProduction Product Item` set transport_payment_done = %s where name = %s", (submit, a.reference_row))
			elif a.reference_type == "Stock Entry":
				frappe.db.sql("update `tabStock Entry` set transport_payment_done = %s where name = %s", (submit, a.reference_name))
			
			elif a.reference_type == "Delivery Note":
				frappe.db.sql("update `tabDelivery Note` set transport_payment_done = %s where name = %s", (submit, a.reference_name))
			
			elif a.reference_type == "Transporter Trip Log":
				frappe.db.sql("update `tabTransporter Trip Log` set transport_payment_done = %s where name = %s", (submit, a.reference_name))

			else:
				pass

		for b in self.pols:
			frappe.db.sql("update tabPOL set transport_payment_done = %s where name = %s", (submit, b.pol))


