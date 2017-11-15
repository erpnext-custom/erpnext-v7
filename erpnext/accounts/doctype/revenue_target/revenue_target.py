# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  SHIV		                   15/11/2017         Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, get_url, today

class RevenueTarget(Document):
        def validate(self):
                self.validate_mandatory()

        def validate_mandatory(self):
                tot_target_amount = 0.0
                
                for item in self.revenue_target_account:
                        if flt(item.target_amount) < 0.0:
                                frappe.throw(_("Row#{0}: Target Amount cannot be a negative value.").format(item.idx), title="Invalid Value")

                        if frappe.db.get_value("Account", item.account, "root_type") <> "Income":
                                frappe.throw(_("Row#{0}: `{1}` is not an Income GL.").format(item.idx, item.account), title="Invalid GL")

                        if not item.account_code:
                                item.account_code = frappe.db.get_value("Account", item.account, "account_code")

                        tot_target_amount += flt(item.target_amount)

                self.tot_target_amount = tot_target_amount
                

