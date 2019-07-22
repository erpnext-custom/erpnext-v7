# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt


class AssetIssueDetails(Document):
	def validate(self):
		bal_qty = 0.0
		query = frappe.db.sql(""" select ae.item_code, (select i.item_name from `tabItem` as i where i.item_code = ae.item_code) 
				as item_name, sum(ae.qty) as total_qty, (select sum(id.qty) from `tabAsset Issue Details` id 
				where id.item_code = ae.item_code and id.docstatus = 1) as issued_qty from `tabAsset Received Entries` as ae 
				where ae.docstatus = 1 and ae.item_code = '{0}'""".format(self.item_code), as_dict = 1)
		bal_qty = flt(query[0].total_qty) - flt(query[0].issued_qty)
		if flt(self.qty) > flt(bal_qty):
			frappe.throw(" Cannot Issue! Balance Qty of Item <b> {0} </b> is <b> {1} </b> Only".format(query[0].item_code, bal_qty))

