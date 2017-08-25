# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EquipmentHiringExtension(Document):
	def on_submit(self):
		self.update_date()

	def update_date(self):
		name = frappe.db.sql("select ha.name from `tabHiring Approval Details` ha, `tabEquipment Hiring Form` h where ha.parent = h.name and h.docstatus = 1 and ha.equipment = %s and h.name = %s", (str(self.equipment), str(self.ehf_name)), as_dict=True)
		if name:
			doc = frappe.get_doc("Hiring Approval Details", name[0]['name'])
			if doc:
				if str(doc.to_date) >= self.extension_date:
					frappe.throw("Extension Date SHOULD be greater than " + str(doc.to_date) )
				else:
					res = frappe.db.get_value("Equipment Reservation Entry", {"equipment": doc.equipment, "ehf_name": doc.parent, "from_date": doc.from_date, "to_date": doc.to_date, "docstatus": 1}, "name")
					ere = frappe.get_doc("Equipment Reservation Entry", res)
					ere.db_set("to_date", self.extension_date)
					doc.db_set("to_date", self.extension_date)
					
					#ehf = frappe.get_doc("Equipment Hiring Form", self.ehf_name)
					#if ehf.private == 'Private':
					#	frappe.throw("Private....ADvance")
		else:
			frappe.throw("Corresponding Hire Approved Detail not found")

