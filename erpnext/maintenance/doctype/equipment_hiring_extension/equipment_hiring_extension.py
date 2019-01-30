# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, date_diff

class EquipmentHiringExtension(Document):
	def validate(self):
		self.update_date()

	def on_submit(self):
		self.update_date(submit=True)

	def before_cancel(self):
		if self.journal:
			ds = frappe.db.get_value("Journal Entry", self.journal, "docstatus")
			if flt(ds) < 2:
				frappe.throw("Cancel the journal entry " + str(self.journal) + " before cancelling")

	def update_date(self, submit=None):
		name = frappe.db.sql("select ha.name from `tabHiring Approval Details` ha, `tabEquipment Hiring Form` h where ha.parent = h.name and h.docstatus = 1 and ha.equipment = %s and h.name = %s", (str(self.equipment), str(self.ehf_name)), as_dict=True)
		if name:
			doc = frappe.get_doc("Hiring Approval Details", name[0]['name'])
			if doc:
				if str(doc.to_date) >= self.extension_date:
					frappe.throw("Extension Date SHOULD be greater than " + str(doc.to_date) )
				else:
					ehf = frappe.get_doc("Equipment Hiring Form", self.ehf_name)
					if submit:
						res = frappe.db.get_value("Equipment Reservation Entry", {"equipment": doc.equipment, "ehf_name": doc.parent, "from_date": doc.from_date, "to_date": doc.to_date, "docstatus": 1}, "name")
						ere = frappe.get_doc("Equipment Reservation Entry", res)
						ere.db_set("to_date", self.extension_date)
						doc.db_set("to_date", self.extension_date)
						
						if ehf.private == 'Private':
							self.post_journal_entry()
					else:
						#self.rate = doc.rate
						self.check_hire_rate(doc)
						if not self.hours:
							days = date_diff(self.extension_date, doc.to_date)
							self.hours = flt(days) * 8
						self.actual_receivable = flt(self.hours) * flt(self.rate) 
						if ehf.private == 'Private':
							balance_advance = frappe.db.sql("select sum(credit_in_account_currency) as amount from `tabJournal Entry Account` where reference_type = 'Equipment Hiring Form' and reference_name = %s and docstatus = 1 and is_advance = 'Yes'", self.ehf_name, as_dict=True)
							if balance_advance:
								self.advance_balance = balance_advance[0].amount
							self.receivable_amount = flt(self.total_amount) + flt(self.advance_balance)
							if flt(self.receivable_amount) <= 0:
								self.receivable_amount = 0
		else:
			frappe.throw("Corresponding Hire Approved Detail not found")

	def check_hire_rate(self, doc):
                based_on = frappe.db.get_single_value("Mechanical Settings", "hire_rate_based_on")
                if not based_on:
                        frappe.throw("Set the <b>Hire Rate Based On</b> in <b>Mechanical Settings</b>")

                if based_on == "Equipment Hiring Form" or doc.tender_hire_rate:
                        self.rate = doc.rate
                        return

                c = frappe.get_doc("Customer", self.customer)
                wf = "a.rate_fuel"
                wof = "a.rate_wofuel"
                ir = "a.idle_rate"

                if c.customer_group == "Internal":
                        wf = "a.rate_fuel_internal"
                        wof = "a.rate_wofuel_internal"
                        ir = "a.idle_rate_internal"

                e = frappe.get_doc("Equipment", self.equipment)

		db_query = "select {0} as rate_fuel, {1} as rate_wofuel, {2} as idle_rate, a.yard_hours, a.yard_distance from `tabHire Charge Item` a, `tabHire Charge Parameter` b where a.parent = b.name and b.equipment_type = '{3}' and b.equipment_model = '{4}' and '{5}' between a.from_date and ifnull(a.to_date, now()) and '{6}' between a.from_date and ifnull(a.to_date, now()) LIMIT 1"
                data = frappe.db.sql(db_query.format(wf, wof, ir, e.equipment_type, e.equipment_model, doc.to_date, self.extension_date), as_dict=True)

                if not data:
                        frappe.throw("There is either no Hire Charge defined or your logbook period overlaps with the Hire Charge period.")
                if doc.rate_type == "With Fuel":
                        self.rate = data[0].rate_fuel
                if doc.rate_type == "Without Fuel":
                        self.rate = data[0].rate_wofuel

	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		if flt(self.total_amount) <= 0:
			return

		advance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_advance_account")
		revenue_bank = frappe.db.get_value("Branch", self.branch, "revenue_bank_account")

		if revenue_bank and advance_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "Advance for Equipment Extension Hire (" + self.ehf_name + ")"
			je.voucher_type = 'Bank Entry'
			je.naming_series = 'Bank Receipt Voucher'
			je.remark = 'Advance payment against : ' + self.name;
			je.posting_date = self.posting_date
			je.branch = self.branch

			je.append("accounts", {
					"account": advance_account,
					"party_type": "Customer",
					"party": self.customer,
					"reference_type": "Equipment Hiring Form",
					"reference_name": self.ehf_name,
					"cost_center": self.cost_center,
					"credit_in_account_currency": flt(self.total_amount),
					"credit": flt(self.total_amount),
					"is_advance": 'Yes'
				})

			je.append("accounts", {
					"account": revenue_bank,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.total_amount),
					"debit": flt(self.total_amount),
				})
			je.insert()
			self.db_set("journal", je.name)
			frappe.msgprint("Posted an advance amount of "+str(self.total_amount)+" for "+str(self.hours)+" hours")
