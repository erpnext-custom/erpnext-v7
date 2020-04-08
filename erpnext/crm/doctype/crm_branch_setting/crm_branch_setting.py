# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt
from frappe.model.document import Document

class CRMBranchSetting(Document):
	def validate(self):
		self.validate_defaults()
		self.update_item_details()

	def validate_defaults(self):
		if frappe.db.exists("CRM Branch Setting", {"name": ("!=", self.name), "branch": self.branch}): 
			old_name = frappe.db.get_value("CRM Branch Setting", {"name": ("!=", self.name), "branch": self.branch}, "name")
			frappe.throw(_("Branch already exists as <b>{0}</b>").format(old_name))
		elif cint(self.has_common_pool) and not cint(self.lead_time): 
			frappe.throw(_("Lead Time is mandatory for branches with common pool facility"))

	def update_item_details(self):
		dup = {}
		for i in self.get("items"):
			item = frappe.get_doc("Item", i.item)
			i.item_name 	 = item.item_name
			i.item_sub_group = item.item_sub_group
			i.uom 		 = item.stock_uom

			if str(i.item) in dup:
				frappe.throw(_("Row#{0}: Duplicate entry for item {1} not permitted").format(i.idx,i.item), title="Invalid Operation")
			else:
				dup.update({str(i.item): 1})

			if flt(i.daily_quantity_limit) or flt(i.weekly_quantity_limit) \
				or flt(i.monthly_quantity_limit) or flt(i.yearly_quantity_limit):
				i.has_limit = 1
				if flt(i.daily_quantity_limit) < 0:
					frappe.throw(_("Row#{0}: Limit/Day cannot be a negative value").format(i.idx))
				elif flt(i.weekly_quantity_limit) < 0:
					frappe.throw(_("Row#{0}: Limit/Week cannot be a negative value").format(i.idx))
				elif flt(i.weekly_quantity_limit) and flt(i.weekly_quantity_limit) < flt(i.daily_quantity_limit):
					frappe.throw(_("Row#{0}: Limit/Week cannot be less than Limit/Day").format(i.idx))
				elif flt(i.monthly_quantity_limit) < 0:
					frappe.throw(_("Row#{0}: Limit/Month cannot be a negative value").format(i.idx))
				elif flt(i.monthly_quantity_limit) and flt(i.monthly_quantity_limit) < flt(i.weekly_quantity_limit):
					frappe.throw(_("Row#{0}: Limit/Month cannot be less than Limit/Week").format(i.idx))
				elif flt(i.monthly_quantity_limit) and flt(i.monthly_quantity_limit) < flt(i.daily_quantity_limit):
					frappe.throw(_("Row#{0}: Limit/Month cannot be less than Limit/Day").format(i.idx))
				elif flt(i.yearly_quantity_limit) < 0:
					frappe.throw(_("Row#{0}: Limit/Year cannot be a negative value").format(i.idx))
				elif flt(i.yearly_quantity_limit) and flt(i.yearly_quantity_limit) < flt(i.monthly_quantity_limit):
					frappe.throw(_("Row#{0}: Limit/Year cannot be less than Limit/Month").format(i.idx))
				elif flt(i.yearly_quantity_limit) and flt(i.yearly_quantity_limit) < flt(i.weekly_quantity_limit):
					frappe.throw(_("Row#{0}: Limit/Year cannot be less than Limit/Week").format(i.idx))
				elif flt(i.yearly_quantity_limit) and flt(i.yearly_quantity_limit) < flt(i.daily_quantity_limit):
					frappe.throw(_("Row#{0}: Limit/Year cannot be less than Limit/Day").format(i.idx))
			else:
				i.has_limit = 0

