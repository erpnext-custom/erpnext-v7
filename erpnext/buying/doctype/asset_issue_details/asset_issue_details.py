# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AssetIssueDetails(Document):
	def on_submit(self):
		asset = frappe.new_doc("Asset")
		asset.item_code = self.item_code
		asset.asset_name = self.item_name 
		asset.branch = self.branch
		asset.purchase_date = self.issued_date
		asset.issued_to = self.issued_to
		asset.asset_quantity_ = self.qty
		asset.asset_rate = self.amount
		asset.default_currency = default_currency
		asset.company = self.company
		
