# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AssetIssueDetails(Document):
	def validate(self):
		self.cost_center = frappe.db.get_value("Cost Center", {"branch":self.branch, "is_disabled": 0, "is_group": 0}, "name")
		self.check_asset_qty()
  
	#added by cety on 14-09-2022
	def check_asset_qty(self):
		if self.qty:
			if self.qty > 1:
				frappe.throw("Issued Quantity cannot be more than 1")
	def on_submit(self):
		item_doc = frappe.get_doc("Item",self.item_code)
		if item_doc.asset_category:
			asset_category = frappe.db.get_value("Asset Category", item_doc.asset_category, "name")
			fixed_asset_account, credit_account=frappe.db.get_value("Asset Category Account", {'parent':asset_category}, ['fixed_asset_account','credit_account'])
			#total_number_of_depreciations = frappe.db.get_value("Asset Category", item_doc.asset_category, "total_number_of depreciations")
			depreciation_percent = frappe.db.get_value("Asset Category", item_doc.asset_category, "depreciation_percent")



		asset = frappe.new_doc("Asset")
		cost_center = frappe.db.get_value("Cost Center", {"branch":self.branch, "is_disabled": 0, "is_group": 0}, "name") 
		asset.item_code = self.item_code
		asset.asset_name = self.item_name
		asset.cost_center =cost_center
		asset.model = self.model
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
		asset.gross_purchase_amount = self.amount
		#asset.total_number_of_depreciations = total_number_of_depreciations
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

