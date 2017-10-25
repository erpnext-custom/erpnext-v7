# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate

class EquipmentHiringForm(Document):
	def validate(self):
		self.check_duplicate()
		self.calculate_totals()

	def before_submit(self):
		if self.private == "Private" and self.advance_amount <= 0:
			frappe.throw("For Private Customers, Advance Amount is Required!")

		if not self.approved_items:
			frappe.throw("Cannot submit hiring form without Approved Items")

	def before_submit(self):
		self.check_equipment_free()

	def on_submit(self):
		self.assign_hire_form_to_equipment()
		if self.advance_amount > 0:
			self.post_journal_entry()

	def before_cancel(self):		
		cl_status = frappe.db.get_value("Journal Entry", self.advance_journal, "docstatus")
		if cl_status != 2:
			frappe.throw("You need to cancel the journal entry related to this job card first!")
	
		frappe.db.sql("delete from `tabEquipment Reservation Entry` where ehf_name = \'"+ str(self.name) +"\'")	
		self.db_set("advance_journal", '')

	def check_duplicate(self):
		for a in self.approved_items:
			for b in self.approved_items:
				if a.equipment == b.equipment and a.idx != b.idx:
					frappe.throw("Duplicate entries for equipments in row " + str(a.idx) + " and " + str(b.idx))

	def calculate_totals(self):
		if self.approved_items:
			total = 0
			for a in self.approved_items:
				total += flt(a.grand_total)
			self.total_hiring_amount = total
			if self.private == "Private":
				self.advance_amount = total
		

	def assign_hire_form_to_equipment(self):
		for a in self.approved_items:
			doc = frappe.new_doc("Equipment Reservation Entry")
			doc.flags.ignore_permissions = 1 
			doc.equipment = a.equipment
			doc.reason = "Hire"
			doc.ehf_name = self.name
			doc.place = a.place
			doc.from_date = a.from_date
			doc.to_date = a.to_date
			doc.hours = a.total_hours
			doc.submit()

	def check_equipment_free(self):
		for a in self.approved_items:
			result = frappe.db.sql("select ehf_name from `tabEquipment Reservation Entry` where equipment = \'" + str(a.equipment) + "\' and docstatus = 1 and (\'" + str(a.from_date) + "\' between from_date and to_date OR \'" + str(a.to_date) + "\' between from_date and to_date)", as_dict=True)
			if result:
				if a.from_time and a.to_time:
					res = frappe.db.sql("select name from `tabHiring Approval Details` where docstatus = 1 and equipment = %s and (%s between from_time and to_time or %s between from_time and to_time)", (str(a.equipment), str(a.from_time), str(a.to_time)))
					if res:
						frappe.throw("The equipment " + str(a.equipment) + " is already in use from by " + str(result[0].ehf_name))
		
	##
	# make necessary journal entry
	##
	def post_journal_entry(self):
		advance_account = frappe.db.get_single_value("Maintenance Accounts Settings", "default_advance_account")
		revenue_bank = frappe.db.get_value("Branch", self.branch, "revenue_bank_account")

		if revenue_bank and advance_account:
			je = frappe.new_doc("Journal Entry")
			je.flags.ignore_permissions = 1 
			je.title = "Advance for Equipment Hire (" + self.name + ")"
			je.voucher_type = 'Bank Entry'
			je.naming_series = 'Bank Receipt Voucher'
			je.remark = 'Advance payment against : ' + self.name;
			je.posting_date = frappe.utils.nowdate()
			je.branch = self.branch

			je.append("accounts", {
					"account": advance_account,
					"party_type": "Customer",
					"party": self.customer,
					"reference_type": "Equipment Hiring Form",
					"reference_name": self.name,
					"cost_center": self.cost_center,
					"credit_in_account_currency": flt(self.advance_amount),
					"credit": flt(self.advance_amount),
					"is_advance": 'Yes'
				})

			je.append("accounts", {
					"account": revenue_bank,
					"cost_center": self.cost_center,
					"debit_in_account_currency": flt(self.advance_amount),
					"debit": flt(self.advance_amount),
				})
			je.insert()
			self.db_set("advance_journal", je.name)

@frappe.whitelist()
def get_hire_rates(e, rtype):
	e = frappe.get_doc("Equipment", e)
	query = "select with_fuel, without_fuel, idle from `tabHire Charge Parameter` where equipment_type = \"" + str(e.equipment_type) + "\" and equipment_model =\"" + str(e.equipment_model) + "\""
	data = frappe.db.sql(query, as_dict=True)
	if not data:
		frappe.throw("No Hire Rates has been assigned for equipment type " + str(e.equipment_type) + " and model " + str(e.equipment_model))
	return data	

@frappe.whitelist()
def get_rates(form, equipment):
	if form and equipment:
		return frappe.db.sql("select rate_type, rate, idle_rate from `tabHiring Approval Details` where docstatus = 1 and parent = \'" + str(form) + "\' and equipment = \'" + str(equipment) + "\'", as_dict=True)

@frappe.whitelist()
def update_status(name):
	so = frappe.get_doc("Equipment Hiring Form", name)
	so.db_set("payment_completed", 1)

def equipment_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("select e.name, e.equipment_type, e.equipment_number from `tabEquipment` e where e.equipment_type = %s and e.branch = %s and e.is_disabled != 1 and e.not_cdcl = 0 and not exists (select 1 from `tabEquipment Reservation Entry` a where (a.from_date != a.to_date and (a.from_date between %s and %s or a.to_date between %s and %s)) and a.equipment = e.name)", (filters['equipment_type'], filters['branch'], filters['from_date'], filters['to_date'], filters['from_date'], filters['to_date']))



