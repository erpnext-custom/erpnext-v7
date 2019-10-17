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
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, get_url, today

class RevenueTarget(Document):
        def validate(self):
                self.validate_mandatory()

        def validate_mandatory(self):
                tot_target_amount     = 0.0
                tot_adjustment_amount = 0.0
                
                for item in self.revenue_target_account:
                        if flt(item.target_amount) < 0.0:
                                frappe.throw(_("Row#{0}: Target Amount cannot be a negative value.").format(item.idx), title="Invalid Value")

                        if frappe.db.get_value("Account", item.account, "root_type") <> "Income":
                                frappe.throw(_("Row#{0}: `{1}` is not an Income GL.").format(item.idx, item.account), title="Invalid GL")

                        if not item.account_code:
                                item.account_code = frappe.db.get_value("Account", item.account, "account_code")
			
			item.net_target_amount = item.target_amount + item.adjustment_amount
                        tot_target_amount     += flt(item.target_amount)
                        tot_adjustment_amount += flt(item.adjustment_amount)

                self.tot_target_amount     = tot_target_amount
                self.tot_adjustment_amount = tot_adjustment_amount
                self.tot_net_target_amount = flt(tot_target_amount) + flt(tot_adjustment_amount)
                
	def get_accounts(self):
                query = "select name as account, account_code from tabAccount where account_type in (\'Income Account\') and is_group = 0 and company = \'" + str(self.company) + "\' and (freeze_account is null or freeze_account != 'Yes')"
                entries = frappe.db.sql(query, as_dict=True)
                self.set('revenue_target_account', [])

                for d in entries:
                        d.initial_budget = 0
                        row = self.append('revenue_target_account', {})
                        row.update(d)
@frappe.whitelist()
def make_adjustment_entry(source_name, target_doc=None):
        doc = get_mapped_doc("Revenue Target", source_name, {
                "Revenue Target": {
                        "doctype": "Revenue Target Adjustment",
                        "validation": {
                                "docstatus": ["=", 1]
                        },
                        "field_map": [
                                ["name", "revenue_target"],
                                ["tot_net_target_amount", "tot_target_amount"],
                                [0, "tot_adjustment_amount"]
                        ]
                },
                "Revenue Target Account": {
                        "doctype": "Revenue Target Adjustment Account",
                        "field_map": [
                                ["parent", "revenue_target"],
                                ["name", "revenue_target_item"],
                                ["net_target_amount", "target_amount"],
                                [0, "adjustment_amount"],
                                ["cost_center", "original_cost_center"],
                                ["account", "original_account"],
                                ["account_code", "original_account_code"],
                                ["net_target_amount", "original_target_amount"]
                        ]
                }
        }, target_doc)

        return doc
