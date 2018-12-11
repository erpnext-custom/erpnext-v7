# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class CurrencyExchange(Document):
	def autoname(self):
		self.name = self.from_currency + "-" + self.to_currency

	def validate(self):
		self.validate_value("exchange_rate", ">", 0)

		if self.from_currency == self.to_currency:
			frappe.throw(_("From Currency and To Currency cannot be same"))

	def on_update(self):
		doc = frappe.new_doc("Exchange Rate History")
		doc.flags.ignore_permissions=1
		doc.from_currency = self.from_currency
		doc.to_currency = self.to_currency
		doc.exchange_rate = self.exchange_rate
		doc.date = frappe.utils.nowdate()
		doc.submit()


