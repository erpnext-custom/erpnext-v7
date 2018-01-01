# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt

class EquipmentPOLTransfer(Document):
	def validate(self):
		if flt(self.quantity) < 1:
			frappe.throw("Quantity cannot be less than 1")

	def on_submit(self):
		self.adjust_consumed_pol()

	def on_cancel(self):
		frappe.db.sql("update `tabConsumed POL` set docstatus = 2 where reference_name = %s", (self.name))
		frappe.db.commit()
	
	def adjust_consumed_pol(self):
		if self.from_equipment and self.to_equipment:
			con = frappe.new_doc("Consumed POL")	
			con.equipment = self.from_equipment
			con.branch = self.from_branch
			con.pol_type = self.pol_type
			con.date = self.transfer_date
			con.qty = 0 - flt(self.quantity)
			con.reference_type = "Equipment POL Transfer"
			con.reference_name = self.name
			con.submit()

			to = frappe.new_doc("Consumed POL")	
			to.equipment = self.to_equipment
			to.branch = self.to_branch
			to.pol_type = self.pol_type
			to.date = self.transfer_date
			to.qty = self.quantity
			to.reference_type = "Equipment POL Transfer"
			to.reference_name = self.name
			to.submit()
		else:
			frappe.throw("Should have both 'From' and 'To' Equipment")



