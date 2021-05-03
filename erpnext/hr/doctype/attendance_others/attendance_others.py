# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AttendanceOthers(Document):
	def on_cancel(self):
                user = frappe.session.user
                if "HR Manager" not in frappe.get_roles(user):
                        frappe.throw("Only HR Manager Can Cancel the document")
