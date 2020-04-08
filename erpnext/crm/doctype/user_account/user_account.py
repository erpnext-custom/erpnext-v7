# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class UserAccount(Document):
	def validate(self):
		pass

	def on_update(self):
		#self.update_customer()
		pass
		
	def update_customer(self):
		""" create/update Customer based on CID """
		if frappe.db.exists("Customer", {"customer_id": self.user}):
			doc = frappe.get_doc("Customer", {"customer_id": self.user})
		else:
			return

		customer_address = [self.full_name, self.billing_address_line1, self.billing_address_line2,
					self.billing_dzongkhag, self.billing_gewog, self.billing_pincode]
		customer_address = [i for i in customer_address if i]
		customer_address = "\n".join(customer_address) if customer_address else doc.customer_details
		doc.customer_name = self.full_name	
		doc.customer_group= "Domestic"
		doc.territory	  = "Bhutan"
		doc.customer_type = "Domestic Customer"
		doc.customer_id	  = self.user
		doc.dzongkhag	  = self.billing_dzongkhag if self.billing_dzongkhag else doc.dzongkhag
		doc.mobile_no	  = self.mobile_no if self.mobile_no else doc.mobile_no
		doc.customer_details = customer_address
		doc.save(ignore_permissions=True)

@frappe.whitelist()
def has_pending_transactions(user):
	return 0
