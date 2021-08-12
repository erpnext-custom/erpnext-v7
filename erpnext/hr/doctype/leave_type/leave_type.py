# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.model.document import Document

class LeaveType(Document):
	def validate(self):
		if self.name == "Casual Leave":
			if self.is_carry_forward:
				frappe.throw("You are not allowed to tick for 'Is Carry Forward' for Casual Leave")
