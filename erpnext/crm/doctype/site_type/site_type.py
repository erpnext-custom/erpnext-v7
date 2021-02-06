# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt
from frappe.model.document import Document

class SiteType(Document):
	def validate(self):
		self.validate_payment_type()
		self.set_default()
		self.validate_advance_settings()

	# following method created by SHIV on 2020/12/30 to accommodate Phase-II
	# advance payment settings are moved to newly created child table
	def validate_advance_settings(self):
		for row in self.get("advances"):
			if cint(row.advance_required) and flt(row.advance_percent) <= 0:
				frappe.throw(_("Row#{}: Advance Percentage should be more than 0 under Advance Pay Settings").format(row.idx))
			elif cint(row.advance_required) and not row.product_category:
				frappe.throw(_("Row#{}: Product Category is mandatory under Advance Pay Settings").format(row.idx))
			elif cint(row.advance_required) and not row.product_group:
				if frappe.db.sql("""select count(*) as count from `tabProduct Category Item`
					where parent = "{}" and product_group is not null
					""".format(row.product_category))[0][0]:
					frappe.throw(_("Row#{}: Product Group is mandatory under Advance Pay Settings").format(row.idx))

	def set_default(self):
		msg = ""
		if not self.is_default and not frappe.db.exists("Site Type", {"is_default": 1}):
			msg = "Site Type <b>{0}</b> is set as default for all the registrations henceforth.\
				You may change it any time".format(self.site_type)
			self.is_default = 1
		elif self.is_default:
			for i in frappe.db.get_all("Site Type", "name", {"name": ("!=", self.name),"is_default": 1}):
				doc = frappe.get_doc("Site Type", i.name)
				doc.is_default = 0
				doc.save(ignore_permissions=True)

			msg = "Site Type <b>{0}</b> is set as default for all the registrations henceforth.\
				You may change it any time".format(self.site_type)

		if msg:
			frappe.msgprint(_(msg))

	def validate_payment_type(self):
		if cint(self.payment_required):
			if self.payment_type == "Flat" and flt(self.min_payment_flat) <= 0:
				frappe.throw(_("<b>Minimum Payment Required (in Flat Amount)</b> must be greater than zero")) 
			elif self.payment_type == "Percent":
				if flt(self.min_payment_percent) <= 0 or flt(self.min_payment_percent) > 100:
					frappe.throw(_("<b>Minimum Payment Required (in %) should be between 1 and 100</b>"))
		if cint(self.credit_allowed) and not self.mode_of_payment:
			frappe.throw(_("Please link a Payment Mode"))
