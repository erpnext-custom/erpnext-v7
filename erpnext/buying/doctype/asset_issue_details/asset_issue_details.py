# this doctype is modified by Birendra as per requirement of client on 24.01.2021
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class AssetIssueDetails(Document):
	def validate(self):
		self.validate_asset_qty()

	def validate_asset_qty(self):
		bal_qty = 0.0
		query = frappe.db.sql(""" select ae.item_code, (select i.item_name from `tabItem` as i where i.item_code = ae.item_code) 
				as item_name, sum(ae.qty) as total_qty, (select sum(id.qty) from `tabAsset Issue Details` id 
				where id.item_code = ae.item_code and id.docstatus = 1) as issued_qty from `tabAsset Received Entries` as ae 
				where ae.docstatus = 1 and ae.item_code = '{0}'""".format(self.item_code), as_dict = 1)
		bal_qty = flt(query[0].total_qty) - flt(query[0].issued_qty)
		if flt(self.qty) > flt(bal_qty):
			frappe.throw(" Cannot Issue! Balance Qty of Item <b> {0} </b> is <b> {1} </b> Only".format(query[0].item_name, bal_qty))

		# qty = frappe.db.sql(
		# 	"""
		# 	SELECT 
		# 		qty
		# 	from 
		# 		`tabAsset Received Entries`
		# 	where 
		# 		docstatus = 1 
		# 	AND item_code = {0}
		# 	""".format(self.item_code), as_dict = 1
		# )
		# if not qty or flt(qty[0].qty) < flt(self.qty):
		# 	frappe.throw("There is not enough {0} in Asset Received Enteries".format(self.item_name))	

	def on_submit(self):
		item_doc = frappe.get_doc("Item",self.item_code)
		if item_doc.asset_category:
			asset_category = frappe.db.get_value("Asset Category", item_doc.asset_category, "name")
			fixed_asset_account, credit_account=frappe.db.get_value("Asset Category Account", {'parent':asset_category}, ['fixed_asset_account','credit_account'])
			#total_number_of_depreciations = frappe.db.get_value("Asset Category", item_doc.asset_category, "total_number_of depreciations")
			depreciation_percent = frappe.db.get_value("Asset Category", item_doc.asset_category, "depreciation_percent")



		asset = frappe.new_doc("Asset")
		cost_center = frappe.db.get_value("Branch", self.branch, "cost_center")
		asset.item_code = self.item_code
		asset.asset_name = self.item_name 
		asset.cost_center =self.cost_center
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

# copy data from backup table
# INSERT INTO `tabAsset Issue Details`(name, creation,modified,modified_by,owner,docstatus,parent,parentfield,parenttype,idx,issued_to,_liked_by,item_name,_comments,_assign,item_code,qty,amended_from,amount,_user_tags,issued_date,branch,cost_center,entry_date) SELECT name, creation,modified,modified_by,owner,docstatus,parent,parentfield,parenttype,idx,issued_to,_liked_by,item_name,_comments,_assign,item_code,qty,amended_from,amount,_user_tags,issued_date,branch,cost_center,entry_date from `copy_asset_issue_details`;