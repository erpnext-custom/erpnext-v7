# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from erpnext.custom_workflow import validate_workflow_states
from frappe.utils import flt

class RequestELAllocation(Document):
	def validate(self):
		validate_workflow_states(self)
		if self.unused_leaves < 1 or self.unused_leaves > 7:
			frappe.throw("Unused No of Leaves to Allocate cannot be less than 1 or greater than 7", title="Error")
		
		#frappe.throw("this is workflow state {0}".format(self.workflow_state.lower()))
		
		if self.workflow_state.lower() == "Approved".lower():
			self.adjust_leave()

	def on_cancel(self):
		self.adjust_leave(1)
		
	def adjust_leave(self, cancel=0):
		le = frappe.get_doc("Employee Group",frappe.db.get_value("Employee", self.employee, "employee_group"))
		las = frappe.db.sql("select name from `tabLeave Allocation` where docstatus = 1 and employee = %s and leave_type = %s and to_date <= %s order by to_date DESC limit 1", (self.employee, self.leave_type, self.posting_date), as_dict=True)
		for l in las:
			doc = frappe.get_doc("Leave Allocation", l.name)
			carry_forwarded = flt(doc.carry_forwarded_leaves) + flt(self.unused_leaves)
			balance = flt(doc.total_leaves_allocated) + flt(self.unused_leaves)
			if cancel:
				carry_forwarded = flt(doc.carry_forwarded_leaves) - flt(self.unused_leaves)
				balance = flt(doc.total_leaves_allocated) - flt(self.unused_leaves)

			if flt(carry_forwarded) > flt(le.encashment_lapse):
				carry_forwarded = le.encashment_lapse
			if flt(balance) > flt(le.encashment_lapse):
				balance = le.encashment_lapse
			doc.db_set("carry_forwarded_leaves", carry_forwarded)
			doc.db_set("total_leaves_allocated", balance)

