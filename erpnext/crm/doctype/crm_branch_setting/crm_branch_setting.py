# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint, flt
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class CRMBranchSetting(Document):
	#Autonaming of doc - added by Kinley Dorji 09/11/2020
	def autoname(self):
		self.name = self.branch+" ("+self.product_category+")"
		if frappe.db.exists("CRM Branch Setting",self.name):
			self.name = make_autoname(self.branch+" ("+self.product_category+ ") .####")
      

	def validate(self):
		self.validate_defaults()
		# self.validate_transportation()
		self.update_item_details()
	
	# following method is created by SHIV on 2020/11/23 to accommodate Phase-II changes
	# def validate_transportation(self):
	# 	if not cint(self.has_common_pool) and not cint(self.allow_self_owned_transport) and not cint(self.allow_other_transport):
	# 		frappe.throw(_("Transport mode should be Common Pool/Self Owned Transport/Others"))

	#Edited to allow multiple branches but with unique product category - Kinley Dorji 09/11/2020 
	def validate_defaults(self):
		if frappe.db.exists("CRM Branch Setting", {"name": ("!=", self.name), "branch": self.branch, "product_category": self.product_category}):
			for doc in frappe.db.sql("""select name from `tabCRM Branch Setting` where name != '{}' and branch = '{}' and product_category = '{}'""".format(self.name, self.branch, self.product_category),as_dict=1):
				# old_name = frappe.db.get_value("CRM Branch Setting", {"name": ("!=", self.name), "branch": self.branch}, "name")
				old_name = doc.name
				old_doc = frappe.get_doc("CRM Branch Setting",old_name)
				for a in old_doc.items:
					for b in self.items:
						if a.item == b.item:
							frappe.throw(_("Branch already exists as <b>{0}</b> for item {1} with Product Category as <b>{2}</b>").format(old_name, b.item, self.product_category))
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

			# Limits
			if i.limit_type == "Quantity" and (flt(i.daily_quantity_limit) or flt(i.weekly_quantity_limit) \
				or flt(i.monthly_quantity_limit) or flt(i.yearly_quantity_limit)):
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
			elif i.limit_type == "Truck Loads" and (flt(i.daily_quantity_limit_count) or flt(i.weekly_quantity_limit_count) \
				or flt(i.monthly_quantity_limit_count) or flt(i.yearly_quantity_limit_count)):
				i.has_limit = 1
				if flt(i.daily_quantity_limit_count) < 0:
					frappe.throw(_("Row#{0}: Limit/Day cannot be a negative value").format(i.idx))
				elif flt(i.weekly_quantity_limit_count) < 0:
					frappe.throw(_("Row#{0}: Limit/Week cannot be a negative value").format(i.idx))
				elif flt(i.weekly_quantity_limit_count) and flt(i.weekly_quantity_limit_count) < flt(i.daily_quantity_limit_count):
					frappe.throw(_("Row#{0}: Limit/Week cannot be less than Limit/Day").format(i.idx))
				elif flt(i.monthly_quantity_limit_count) < 0:
					frappe.throw(_("Row#{0}: Limit/Month cannot be a negative value").format(i.idx))
				elif flt(i.monthly_quantity_limit_count) and flt(i.monthly_quantity_limit_count) < flt(i.weekly_quantity_limit_count):
					frappe.throw(_("Row#{0}: Limit/Month cannot be less than Limit/Week").format(i.idx))
				elif flt(i.monthly_quantity_limit_count) and flt(i.monthly_quantity_limit_count) < flt(i.daily_quantity_limit_count):
					frappe.throw(_("Row#{0}: Limit/Month cannot be less than Limit/Day").format(i.idx))
				elif flt(i.yearly_quantity_limit_count) < 0:
					frappe.throw(_("Row#{0}: Limit/Year cannot be a negative value").format(i.idx))
				elif flt(i.yearly_quantity_limit_count) and flt(i.yearly_quantity_limit_count) < flt(i.monthly_quantity_limit_count):
					frappe.throw(_("Row#{0}: Limit/Year cannot be less than Limit/Month").format(i.idx))
				elif flt(i.yearly_quantity_limit_count) and flt(i.yearly_quantity_limit_count) < flt(i.weekly_quantity_limit_count):
					frappe.throw(_("Row#{0}: Limit/Year cannot be less than Limit/Week").format(i.idx))
				elif flt(i.yearly_quantity_limit_count) and flt(i.yearly_quantity_limit_count) < flt(i.daily_quantity_limit_count):
					frappe.throw(_("Row#{0}: Limit/Year cannot be less than Limit/Day").format(i.idx))
			else:
				i.has_limit = 0

@frappe.whitelist()
def get_items(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
        from erpnext.controllers.queries import get_match_cond

	if not filters.get("product_category"):
		frappe.throw(_("Please select a Product Category first"))

	return frappe.db.sql("""
			select name, item_name, stock_uom
			from `tabItem` i
			where exists(select 1
				from `tabProduct Category Item` pci
				where pci.parent = '{product_category}'
				and pci.item_sub_group = i.item_sub_group)
			and ({key} like %(txt)s
				or item_name like %(txt)s
				or stock_uom like %(txt)s)
			{mcond}
			order by
				if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
				if(locate(%(_txt)s, item_name), locate(%(_txt)s, item_name), 99999),
				if(locate(%(_txt)s, stock_uom), locate(%(_txt)s, stock_uom), 99999),
				idx desc,
				name, item_name, stock_uom
			limit %(start)s, %(page_len)s""".format(**{
				'key': searchfield,
				'mcond': get_match_cond(doctype),
				'product_category': filters.get("product_category")
			}), {
				'txt': "%%%s%%" % txt,
				'_txt': txt.replace("%", ""),
				'start': start,
				'page_len': page_len
	})

