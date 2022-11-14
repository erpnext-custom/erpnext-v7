# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cstr, flt, fmt_money, formatdate, getdate, now_datetime

class AssetIssueDetails(Document):
	def validate(self):
		pass

	def on_submit(self):
		self.check_qty_balance()
		self.make_asset()
  	
	def on_cancel(self):
		if self.reference_code:
			asset_status = frappe.db.get_value("Asset", self.reference_code, 'docstatus')
			if asset_status < 2:
				frappe.throw("You cannot cancel the document before cancelling asset with code {0}".format(self.reference_code))    
    
	def check_qty_balance(self):
		total_qty = frappe.db.sql("""select sum(ifnull(qty,0)) total_qty 
									from `tabAsset Received Entries`
									where item_code="{}"
									and ref_doc = "{}"
									and docstatus = 1
						""".format(self.item_code, self.purchase_receipt))[0][0]
		issued_qty = frappe.db.sql("""select sum(ifnull(qty,0)) issued_qty
									from `tabAsset Issue Details` 
									where item_code ='{}'
									and branch = '{}'
									and purchase_receipt = '{}'
									and docstatus = 1 
									and name != '{}'
						""".format(self.item_code, self.branch, self.purchase_receipt, self.name))[0][0]
		
		balance_qty = flt(total_qty) - flt(issued_qty)
		if flt(self.qty) > flt(balance_qty):
			frappe.throw(_("Issuing Quantity cannot be greater than Balance Quantity i.e., {}").format(flt(balance_qty)), title="Insufficient Balance")
    
	def make_asset(self):
		item_doc = frappe.get_doc("Item",self.item_code)
		if item_doc.asset_category:
			asset_category = frappe.db.get_value("Asset Category", item_doc.asset_category, "name")
			fixed_asset_account, credit_account=frappe.db.get_value("Asset Category Account", {'parent':asset_category}, ['fixed_asset_account','credit_account'])
			#total_number_of_depreciations = frappe.db.get_value("Asset Category", item_doc.asset_category, "total_number_of depreciations")
			depreciation_percent = frappe.db.get_value("Asset Category", item_doc.asset_category, "depreciation_percent")
		asset = frappe.new_doc("Asset")
		asset.item_code = self.item_code
		asset.asset_name = self.item_name
		asset.cost_center = self.cost_center
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
    
@frappe.whitelist()
def check_item_code(doctype, txt, searchfield, start, page_len, filters):
    cond = ""
    if not filters.get('item_code'):
        frappe.throw("Please select Item Code to fetch Purchase Receipt")
    if not filters.get("cost_center"):
        frappe.throw("Please select Branch or Cost Center first.")
    if filters.get('item_code'):
        cond += " ar.item_code = '{}'".format(filters.get('item_code'))
        cond += " and ar.cost_center = '{}'".format(filters.get("cost_center"))
    query = "select ar.ref_doc from `tabAsset Received Entries` ar where {cond}".format(cond=cond)
    
    return frappe.db.sql(query)

