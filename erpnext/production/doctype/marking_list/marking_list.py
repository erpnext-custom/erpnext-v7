# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from erpnext.custom_utils import check_future_date, get_branch_cc, get_settings_value

class MarkingList(Document):
	def validate(self):
		check_future_date(self.posting_date)
		self.validate_items()

	def on_update(self):
		pass
		#self.calculate_total()
		
	def validate_items(self):
		if self.production_type == "Planned":
			if not self.block:
				frappe.throw("Block is mandatory")
			self.adhoc_production = None
		else:
			if not self.adhoc_production:
				frappe.throw("Adhoc Production is mandatory")
			self.block = None
			self.block_name = None

		self.cost_center = get_branch_cc(self.branch)
		total_amount = total_qty_m3 = total_qty_cft = log_volume = firewood_volume = 0
		for d in self.items:
			if not flt(d.qty_m3) > 0:
				frappe.throw("Volume cannot be zero or less")
			if not flt(d.diameter) > 0:
				frappe.throw("Diameter cannot be zero or less")

			doc = frappe.get_doc("Timber Species", d.species)
			d.timber_type = doc.timber_type
			d.timber_class = doc.timber_class

			d.qty_cft = d.qty_m3 * 35.315
			total_qty_m3 += d.qty_m3
			total_qty_cft += d.qty_cft

			if d.timber_type == "Conifer":
				d.log_percent = get_settings_value("Production Settings", self.company, "log_percent_conifer")
				d.firewood_percent = get_settings_value("Production Settings", self.company, "firewood_percent_conifer")
			else:
				d.log_percent = get_settings_value("Production Settings", self.company, "log_percent_broadleaf")
				d.firewood_percent = get_settings_value("Production Settings", self.company, "firewood_percent_broadleaf")
			if not d.log_percent or not d.firewood_percent:
				frappe.throw("Log and Firewood Percent Not Defined in Production Settings")
			log_volume += d.qty_cft * flt(d.log_percent)/100
			firewood_volume += d.qty_m3 * flt(d.firewood_percent)/100
	
			if self.production_type == "Adhoc":
				continue

			#Change this to get from class
			royalty_rates = frappe.db.sql("select log_rate, fw_soft_rate, fw_hard_rate from `tabRoyal Rate` where %s between from_date and ifnull(to_date, now()) and parent = %s", (self.posting_date, d.timber_class), as_dict=1)
			if not royalty_rates:
				frappe.throw("Royalty Rate not defined. Please define in Timber Class")
			d.log_rate = flt(royalty_rates[0].log_rate)
			if d.timber_type == "Conifer":
				d.firewood_rate = flt(royalty_rates[0].fw_soft_rate)
			else:
				d.firewood_rate = flt(royalty_rates[0].fw_hard_rate)

			d.log_amount = d.qty_cft * d.log_rate * flt(d.log_percent)/100 
			d.firewood_amount = d.qty_m3 * d.firewood_rate * flt(d.firewood_percent)/100 
			
			d.royalty_amount = d.log_amount + d.firewood_amount
			total_amount += d.royalty_amount

		self.total_amount = total_amount
		self.total_qty_m3 = total_qty_m3
		self.total_qty_cft = total_qty_cft
		self.log_volume = log_volume
		self.firewood_volume = firewood_volume

	def calculate_total(self):
		#records = frappe.db.sql("select b.class as timber_class, sum(a.qty) as qty_m3, b.timber_type from `tabMarking List Item` a, `tabTimber Species` b where a.species = b.name and a.parent = %s group by b.class, b.timber_type", self.name, as_dict=1)
		records = frappe.db.sql("select a.species, b.class as timber_class, sum(a.qty) as qty_m3, b.timber_type from `tabMarking List Item` a, `tabTimber Species` b where a.species = b.name and a.parent = %s group by a.species", self.name, as_dict=1)
		self.set('aggregate_items', [])
		#frappe.db.sql("delete from `tabMarking List Aggregate` where parent = %s", self.name)
		frappe.db.sql("delete from `tabMarking List Details` where parent = %s", self.name)

		total_amount = 0
                for d in records:
			d.qty_cft = d.qty_m3 * 35.315
			if d.timber_type == "Conifer":
				d.log_percent = get_settings_value("Production Settings", self.company, "log_percent_conifer")
				d.firewood_percent = get_settings_value("Production Settings", self.company, "firewood_percent_conifer")
			else:
				d.log_percent = get_settings_value("Production Settings", self.company, "log_percent_broadleaf")
				d.firewood_percent = get_settings_value("Production Settings", self.company, "firewood_percent_broadleaf")
			
			#Change this to get from class
			royalty_rates = frappe.db.sql("select log_rate, firewood_rate from `tabRoyal Rate` where %s between from_date and ifnull(to_date, now()) and parent = %s", (self.posting_date, d.timber_class), as_dict=1)
			if not royalty_rates:
				frappe.throw("Royalty Rate not defined. Please define in Timber Class")
			d.log_rate = flt(royalty_rates[0].log_rate)
			d.firewood_rate = flt(royalty_rates[0].firewood_rate)

			d.log_amount = d.qty_cft * d.log_rate * flt(d.log_percent)/100 
			d.firewood_amount = d.qty_m3 * d.firewood_rate * flt(d.firewood_percent)/100 
			
			d.royalty_amount = d.log_amount + d.firewood_amount
			total_amount += d.royalty_amount
	
                        row = self.append('aggregate_items', {})
                        row.update(d)
			row.save()

		if total_amount <= 0:
			frappe.throw("Total Royalty Amount cannot be zero or less")
		self.db_set("total_amount", total_amount)
		frappe.reload_doctype(self.doctype)

	def on_submit(self):
		self.validate_items()
		pass

	def make_royalty_payment(self):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Royalty payment for (" + self.fmu + ")"
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
				"reference_type": "Marking List",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.total_amount),
				"debit": flt(self.total_amount),
				"business_activity": self.business_activity
			})

		je.append("accounts", {
				"account": bank_account,
				"reference_type": "Marking List",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_amount),
				"credit": flt(self.total_amount),
				"business_activity": self.business_activity
			})
		je.save()
		self.db_set("journal_entry", je.name)
		frappe.reload_doctype(self.doctype)

