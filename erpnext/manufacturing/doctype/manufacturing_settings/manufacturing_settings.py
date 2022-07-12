# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint
from dateutil.relativedelta import relativedelta

class ManufacturingSettings(Document):
	def validate(self):
		item_list = []
		for d in self.get("items"):
			if d.item not in item_list:
				item_list.append(d.item)
			else:
				frappe.throw("Item {0} duplicate at #Row {1}".format(d.item, d.idx))

def get_mins_between_operations():
	return relativedelta(minutes=cint(frappe.db.get_single_value("Manufacturing Settings",
		"mins_between_operations")) or 10)
