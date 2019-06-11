# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class RentalBill(Document):
	def autoname(self):
                customer_code = frappe.db.get_value("Customer", {"customer_id":self.tenant}, "customer_code")
                bill_code = "NHDCL/" + customer_code + "/" + self.fiscal_year + self.month + '/.#####'

		self.name = make_autoname(bill_code)	
