# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate, getdate, get_datetime
from frappe.desk.reportview import get_match_cond
from erpnext.custom_utils import check_uncancelled_linked_doc, check_future_date

class EquipmentHiringForm(Document):
	def validate(self):
		self.validate_date()
		#self.validate_amount()
		self.validate_supplier()
		self.validate_data()
	
	def validate_update_after_submit(self):
		efh_extension_count = frappe.db.sql("select count(*) from `tabEHF Extension` where parent = '{}'".format(self.name))
		efh_rate_count = frappe.db.sql("select count(*) from `tabEHF Rate` where parent = '{}'".format(self.name))
		extension_count = rate_count = 0
		for a in self.get('efh_extension'):
			extension_count += 1
		
		if extension_count < efh_extension_count[0][0]:
			frappe.throw("You are not allowed to <b>remove the record in Extension table</b>. Please reload to load the record again")

		for b in self.get('ehf_rate'):
			rate_count += 1
			if not b.name:
				if b.from_date > b.to_date:
					frappe.throw("From Date cannot be after to Date")
				check = frappe.db.sql("""select count(*) 
									from `tabEHF Rate` where ('{}' between from_date and to_date 
									or '{}' between from_date and to_date)
									and parent = '{}'
									""".format(b.from_date, b.to_date, self.name))
				if check[0][0] > 0:
					frappe.throw("Row ID : <b>{} </b>date range {} and {} is already defined.".format(b.idx, b.from_date, b.to_date))

		if rate_count < efh_rate_count[0][0]:
			frappe.throw("You are not allowed to <b>remove the record in Rate table</b>. Please reload to load the record again")
	
	def on_update_after_submit(self):
		for a in self.get('efh_extension'):
			if not a.hiring_end_date:
				if a.hiring_extended_till > self.end_date:
					a.hiring_end_date = self.end_date
					frappe.db.sql("update `tabEHF Extension` set hiring_end_date='{}' where name='{}'".format(self.end_date, a.name))
					self.db_set("end_date", a.hiring_extended_till)
				else:
					frappe.throw("Equipment Hiring End date is already after the extension date {}".format(a.hiring_extended_till))

		frappe.db.commit()
		#self.update_hiring_history()

	def validate_date(self):
		if self.start_date > self.end_date:
			frappe.throw("Start Date cannot be greater than End Date")
	'''
	def validate_amount(self):
		if not self.rate > 0:
			frappe.throw("Hiring Rate should be greater than zero")
	'''
	
	def validate_supplier(self):
		if not self.supplier:
			frappe.throw("Setup supplier in Equipment Master")

	def validate_data(self):
		is_disabled = frappe.db.get_value("Branch", self.branch, "is_disabled")
		if is_disabled:
			frappe.throw("Cannot use a disabled branch in transaction")

		eqp = frappe.db.get_values("Equipment", self.equipment, ["branch", "is_disabled"], as_dict=1)
		if eqp[0].is_disabled:
			frappe.throw("Cannot use a disabled Equipment in transaction")
		
		if self.branch != eqp[0].branch:
			frappe.throw("Cannot use equipments from other branch")

	# #added by cety
	# def on_submit(self):
	# 	row = self.append('hiring_rate_history', {})
	# 	for item in self.ehf_rate:
	# 		row.modified_by1 = frappe.session.user
	# 		row.hiring_rate = item.hiring_rate
	# 		row.from_date = item.from_date
	# 		row.to_date = item.to_date
	# 	row.save()

	# def update_hiring_history(self):
	# 	row = self.append('hiring_rate_history', {})
	# 	for item in self.ehf_rate:
	# 		row.modified_by1 = frappe.session.user
	# 		row.hiring_rate = item.hiring_rate
	# 		row.from_date = item.from_date
	# 		row.to_date = item.to_date
	# 	row.save()