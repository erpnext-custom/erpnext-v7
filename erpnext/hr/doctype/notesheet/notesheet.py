# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Notesheet(Document):
    # def get_full_user_name(user=None):
    #     p = frappe.db.get_value("User", user, "first_name")
    #     frappe.throw("p:{}".format(p))
    #     return p  

    def validate(self):
        self.validation()

    def validation(self):
        if self.workflow_state == "Waiting Approval":
            if self.owner != frappe.session.user:
                frappe.throw("Only the creator of this notesheet can Apply!")

        # session_log_on = frappe.session.user
        # frappe.throw("session_user:{}".format(session_log_on))

        approver = frappe.db.get_value("HR Settings", self.name, "notesheet_approver_name")
        #frappe.msgprint("Approver:{}".format(approver))
        self.approver = approver

  