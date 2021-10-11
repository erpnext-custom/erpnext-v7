# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class AssetIssueDetails(Document):
	def validate(self):
		pass
	def on_submit(self):
		item_doc = frappe.get_doc("Item",self.item_code)
		if item_doc.asset_category:
			asset_category = frappe.db.get_value("Asset Category", item_doc.asset_category, "name")
			fixed_asset_account, credit_account=frappe.db.get_value("Asset Category Account", {'parent':asset_category}, ['fixed_asset_account','credit_account'])
			if item_doc.asset_sub_category:
				for a in frappe.db.sql("select total_number_of_depreciations, depreciation_percent from `tabAsset Sub Category` where parent = '{0}' and `sub_category_name`='{1}'".format(asset_category, item_doc.asset_sub_category), as_dict=1):
					total_number_of_depreciations = a.total_number_of_depreciations
					depreciation_percent = a.depreciation_percent
		
		asset = frappe.new_doc("Asset")
		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		asset.item_code = self.item_code
		asset.asset_name = self.item_name 
		asset.cost_center = cost_center
		asset.branch = self.branch
		asset.purchase_date = self.issued_date
		asset.next_depreciation_date = self.issued_date
		asset.credit_account = credit_account
		asset.asset_account = fixed_asset_account
		asset.issued_to = self.issued_to
		asset.brand = self.brand
		asset.serial_number = self.serial_number
		asset.asset_quantity_ = self.qty
		asset.asset_rate = self.asset_rate
		asset.business_activity = self.business_activity
		asset.company = self.company
		asset.gross_purchase_amount = self.amount
		asset.total_number_of_depreciations = total_number_of_depreciations
		asset.asset_depreciation_percent = depreciation_percent
		asset.insert()
		frappe.db.commit()

		asset_code = frappe.db.get_value("Asset", {'item_code':self.item_code, 'docstatus': 0, 'issued_to':self.issued_to, 'branch':self.branch}, 'name')
		if asset_code:
			frappe.db.sql("update `tabAsset Issue Details` set reference_code=%s where name=%s",(asset_code, self.name))
		else:
			frappe.throw("Asset not able to create for asset issue no.".format(self.name))
	
	def on_cancel(self):
		if self.reference_code:
			asset_status = frappe.db.get_value("Asset", self.reference_code, 'docstatus')
			if asset_status < 2:
				frappe.throw("You cannot cancel the document before cancelling asset with code {0}".format(self.reference_code))
			else:
				frappe.db.sql("update `tabAsset Issue Details` set reference_code = '' where name='{0}'".format(self.name))

@frappe.whitelist()
def check_item_code(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
    cond = ""
    if filters.get('item_code'):
        cond += " item_code = '{}'".format(filters.get('item_code'))
    query = "select ref_doc from `tabAsset Received Entries` where {cond}".format(cond=cond)
 
    return frappe.db.sql(query)