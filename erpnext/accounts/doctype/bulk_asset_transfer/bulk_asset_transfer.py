# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BulkAssetTransfer(Document):
	def on_submit(self):
		if not self.custodian or not self.custodian_cost_center or not self.custodian_branch:
			frappe.throw("The custodian doesn't have Cost Center and Branch defined in Employee Master")

		for a in self.items:
			doc = frappe.get_doc("Asset", a.asset_code)
			doc.db_set("issued_to", self.custodian)
			doc.db_set("cost_center", self.custodian_cost_center)
			doc.db_set("branch", self.custodian_branch)

	def get_assets(self):
		if not self.purpose:
			frappe.throw("Select a Purpose first!")
		if self.cost_center and self.purpose == "Cost Center":
			entries = frappe.db.sql("select name as asset_code, asset_name, gross_purchase_amount as gross_amount from tabAsset where cost_center = %s", self.cost_center, as_dict=True)
		elif self.current_custodian and self.purpose == "Custodian":
			entries = frappe.db.sql("select name as asset_code, asset_name, gross_purchase_amount as gross_amount from tabAsset where issued_to = %s", self.current_custodian, as_dict=True)
		else:
			frappe.throw("Either select Cost Center or Custodian")
		self.set('items', [])

		for d in entries:
			row = self.append('items', {})
			row.update(d)
