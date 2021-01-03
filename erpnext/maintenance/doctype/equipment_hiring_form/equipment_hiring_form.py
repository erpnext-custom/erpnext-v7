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
		self.validate_amount()
		self.validate_supplier()
		self.validate_data()

	def validate_date(self):
		if self.start_date > self.end_date:
			frappe.throw("Start Date cannot be greater than End Date")

	def validate_amount(self):
		if not self.rate > 0:
			frappe.throw("Hiring Rate should be greater than zero")
	
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
