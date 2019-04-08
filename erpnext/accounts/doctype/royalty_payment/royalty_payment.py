# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.custom_utils import check_future_date, get_branch_cc, prepare_gl, prepare_sl, get_settings_value

class RoyaltyPayment(Document):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_data()

	def validate_data(self):
		if self.production_type == "Planned":
			if not self.marking_list:
				frappe.throw("Marking List is mandatory")
			
			if not self.planned_items:
				frappe.throw("Royalty Details is mandatory")
			self.adhoc_production = None
			self.adhoc_items = []
			self.adhoc_temp_items = []
		else:
			if not self.adhoc_production:
				frappe.throw("Adhoc Production is mandatory")
			self.marking_list = None
			self.planned_items = []

	def get_royalty_details(self):
		if self.production_type == "Planned":
			if not self.marking_list:
				frappe.throw("Marking List is Mandatory")
			entries = frappe.db.sql("select timber_class, timber_type, sum(qty_m3) as qty_m3, sum(qty_cft) as qty_cft, log_rate, log_percent, sum(log_amount) as log_amount, firewood_rate, firewood_percent, sum(firewood_amount) as firewood_amount, sum(royalty_amount) as royalty_amount from `tabMarking List Details` where parent = %s and docstatus = 1 group by timber_class, timber_type order by timber_class", self.marking_list, as_dict=1)

			self.set("planned_items", [])

			total_royalty = total_m3 = total_cft = log_amount = timber_amount = total_log = total_timber = 0
			for d in entries:
				row = self.append('planned_items', {})
				row.update(d)
				total_royalty += d.royalty_amount
				total_m3 += d.qty_m3
				total_cft += d.qty_cft
				log_amount += d.log_amount
				timber_amount += d.firewood_amount 
				total_log += d.qty_cft * d.log_percent / 100
				total_timber += d.qty_m3 * d.firewood_percent / 100

			self.set_total(total_royalty, total_m3, total_cft, log_amount, timber_amount, total_log, total_timber)
		else:
			if not self.adhoc_production or not self.from_date or not self.to_date:
				frappe.throw("Adhoc Production, From Date and To Date are Mandatory")

			entries = frappe.db.sql("select a.name, b.item_code, b.reading, sum(b.qty) as qty, b.uom, b.item_sub_group, sum(b.qty_in_no) as qty_in_no, b.reading_inches from `tabProduction` a, `tabProduction Product Item` b where a.name = b.parent and a.branch = %s and a.adhoc_production = %s and a.posting_date between %s and %s and a.docstatus = 1 and a.royalty_paid = 0 group by b.item_code, b.reading", (self.branch, self.adhoc_production, self.from_date, self.to_date), as_dict=1)
			self.set('adhoc_temp_items', [])
			# Following line replaced by subsequent, by SHIV on 2018/11/13
			#frappe.db.sql("delete from `tabRoyalty Adhoc Temp` where parent = %s or parent like '%New Royalty Payment%'", self.name)
			frappe.db.sql("delete from `tabRoyalty Adhoc Temp` where parent = %s or parent like %s", (self.name,("%" + "New Royalty Payment" + "%")))

			for a in entries:
				d = self.get_adhoc_royalty(a.item_code, a.reading_inches)
				if d[0].based_on == "Item Sub Group":
					d[0].par_name = frappe.db.get_value(d[0].based_on, d[0].particular, "reading_parameter")
				d[0].qty = a.qty
				if a.item_sub_group == "Pole":
					d[0].qty = a.qty_in_no
				d[0].uom = a.uom
				d[0].reference_document = a.name
				d[0].amount = a.qty * d[0].royalty_rate

				row = self.append('adhoc_temp_items', {})
				row.update(d[0])
				row.save()

			entries = frappe.db.sql("select based_on, particular, timber_class, royalty_rate as rate, from_reading, to_reading, sum(qty) as quantity, uom, sum(amount) as amount, par_name from `tabRoyalty Adhoc Temp` where parent = %s group by particular, timber_class, royalty_rate, from_reading, to_reading order by particular", self.name, as_dict=1)
			self.set('adhoc_items', [])
			# Following line replaced by subsequent, by SHIV on 2018/11/13
			#frappe.db.sql("delete from `tabRoyalty Payment Adhoc` where parent = %s or parent like '%New Royalty Payment%'", self.name)
			frappe.db.sql("delete from `tabRoyalty Payment Adhoc` where parent = %s or parent like %s", (self.name,("%" + "New Royalty Payment" + "%")))

			total_royalty = 0
			for a in entries:
				row = self.append('adhoc_items', {})
				if a.based_on == "Item":
					a.particular = frappe.db.get_value("Item", a.particular, "item_name")
				if a.par_name:
					a.reading = str(a.par_name) + " : " + str(a.from_reading) + " to " + str(a.to_reading)
				row.update(a)
				row.save()
				total_royalty += a.amount
			self.set_total(total_royalty)

	def get_adhoc_royalty(self, item_code, reading):
		sub_group, species = frappe.db.get_value("Item", item_code, ["item_sub_group", "species"])

		if species:
			timber_class = frappe.db.get_value("Timber Species", species, "timber_class")
		if reading < 1:
			rate = frappe.db.sql("select based_on, particular, royalty_rate, timber_class, from_reading, to_reading from `tabAdhoc Royalty Setting` a, `tabAdhoc Royalty Setting Item` b where particular = %s and %s between from_date and to_date and timber_class=''", (item_code, self.posting_date), as_dict=1)
		
		if not rate:
			rate = frappe.db.sql("select based_on, particular, royalty_rate, timber_class, from_reading, to_reading from `tabAdhoc Royalty Setting` a, `tabAdhoc Royalty Setting Item` b where particular = %s and %s between from_date and to_date", (item_code, self.posting_date), as_dict=1)
		if not rate:
			rate = frappe.db.sql("select based_on, particular, royalty_rate, timber_class, from_reading, to_reading from `tabAdhoc Royalty Setting` a, `tabAdhoc Royalty Setting Item` b where particular = %s and %s between from_date and to_date and timber_class = %s and %s >= from_inch and %s <= to_inch", (sub_group, self.posting_date, timber_class, reading, reading), as_dict=1, debug=1)
		if not rate:
			frappe.throw("Royalty Rate for {0} has not been defined in Adhoc Royalty Setting".format(frappe.bold(item_code)))
		
		return rate

	def set_total(self, total_royalty=0, total_m3=0, total_cft=0, log_amount=0, timber_amount=0, total_log=0, total_timber=0):
		self.db_set("total_royalty", total_royalty)
		self.db_set("total_m3", total_m3)
		self.db_set("total_cft", total_cft)
		self.db_set("log_amount", log_amount)
		self.db_set("timber_amount", timber_amount)
		self.db_set("total_log", total_log)
		self.db_set("total_timber", total_timber)

	def on_submit(self):
		self.update_production()
		self.make_royalty_payment()

	def on_cancel(self):
		self.update_production()

	def update_production(self):
		if self.production_type == "Planned":
			return

		if self.docstatus == 1:
			r_paid = 1
		else:
			r_paid = 0

		for a in frappe.db.sql("select reference_document from `tabRoyalty Adhoc Temp` where parent = %s group by reference_document", self.name, as_dict=1):
			doc = frappe.get_doc("Production", a.reference_document)
			if r_paid and doc.royalty_paid == 1:
				frappe.throw("Royalty for {0} has already been paid. Reload the Royalty Details again".format(frappe.bold(doc.name)))
			if doc.docstatus == 2:
				frappe.throw("{0} is a cancelled document. Please reload the royalty details again".format(frappe.bold(doc.name)))
			doc.db_set("royalty_paid", r_paid)

	def make_royalty_payment(self):
		if not self.total_royalty:
			frappe.throw("Total Royalty Amount is Mandatory")	
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Royalty payment for " + self.location + " (" + self.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Payment against : ' + self.name;
		je.posting_date = frappe.utils.nowdate()
		je.branch = self.branch

		royalty_account = frappe.db.get_value("Production Account Settings", self.company, "default_royalty_account")
		if not royalty_account:
			frappe.throw("Setup Default Royalty Account in Production Account Settings")	

		bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not bank_account:
			frappe.throw("Setup Expense Bank Account in Branch")	

		je.append("accounts", {
				"account": royalty_account,
				"reference_type": self.doctype,
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.total_royalty),
				"debit": flt(self.total_royalty),
				"business_activity": self.business_activity
			})

		je.append("accounts", {
				"account": bank_account,
				"reference_type": self.doctype,
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_royalty),
				"credit": flt(self.total_royalty),
				"business_activity": self.business_activity
			})
		je.save()
		self.db_set("journal_entry", je.name)
		frappe.reload_doctype(self.doctype)
