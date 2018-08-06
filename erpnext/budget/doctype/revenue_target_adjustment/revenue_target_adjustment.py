# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, get_url, today, nowdate

class RevenueTargetAdjustment(Document):
        def validate(self):
                self.validate_mandatory()

        def on_submit(self):
                self.update_revenue_target()

        def on_cancel(self):
                self.update_revenue_target()

        def update_revenue_target(self):
                tot_target_amount     = 0
                tot_adjustment_amount     = 0
                for i in self.revenue_target_adjustment_account:
                        target_amount     = 0
                        adjustment_amount = 0
                        if i.revenue_target:
                                if i.adjustment_amount:
                                        adjustment_amount         = -1*flt(i.adjustment_amount) if self.docstatus == 2 else flt(i.adjustment_amount)
                                        rta_doc                   = frappe.get_doc("Revenue Target Account", i.revenue_target_item)
                                        rta_doc.adjustment_amount = flt(rta_doc.adjustment_amount) + flt(adjustment_amount)
                                        rta_doc.net_target_amount = flt(rta_doc.net_target_amount) + flt(adjustment_amount)
                                        rta_doc.save(ignore_permissions = True)
                        else:
                                if self.docstatus == 2:
                                        rta_doc = frappe.get_doc("Revenue Target Account", {"reference": i.parent, "reference_item": i.name})
                                        #rta_doc.target_amount     = flt(rta_doc.target_amount) - flt(i.target_amount)
                                        rta_doc.adjustment_amount = flt(rta_doc.adjustment_amount) - flt(i.adjustment_amount)
                                        rta_doc.net_target_amount = flt(rta_doc.net_target_amount) - flt(i.target_amount) - flt(i.adjustment_amount)
                                        rta_doc.save(ignore_permissions = True)
                                        frappe.db.set_value("Revenue Target Account", rta_doc.name, "target_amount", flt(rta_doc.target_amount) - flt(i.target_amount))
                                        
                                        target_amount     = -1*flt(i.target_amount)
                                        adjustment_amount = -1*flt(i.adjustment_amount) 
                                else:
                                        if i.target_amount or i.adjustment_amount:
                                                rt_doc                = frappe.get_doc("Revenue Target", self.revenue_target)
                                                row                   = rt_doc.append("revenue_target_account", {})
                                                row.cost_center       = i.cost_center
                                                row.account           = i.account
                                                row.account_code      = i.account_code
                                                row.remarks           = i.remarks
                                                row.target_amount     = i.target_amount
                                                row.adjustment_amount = i.adjustment_amount
                                                row.net_target_amount = i.net_target_amount
                                                row.reference         = i.parent
                                                row.reference_item    = i.name
                                                row.docstatus         = 1
                                                row.save()

                                                target_amount         = flt(i.target_amount) 
                                                adjustment_amount     = flt(i.adjustment_amount)

                        tot_target_amount     += target_amount
                        tot_adjustment_amount += adjustment_amount

                if tot_target_amount or tot_adjustment_amount:
                        rt_doc = frappe.get_doc("Revenue Target", self.revenue_target)
                        rt_doc.tot_target_amount     = flt(rt_doc.tot_target_amount) + flt(tot_target_amount)
                        rt_doc.tot_adjustment_amount = flt(rt_doc.tot_adjustment_amount) + flt(tot_adjustment_amount)
                        rt_doc.tot_net_target_amount = flt(rt_doc.tot_net_target_amount) + flt(tot_target_amount) + flt(tot_adjustment_amount)
                        rt_doc.save(ignore_permissions = True)
                        
        def validate_mandatory(self):
                tot_target_amount     = 0.0
                tot_adjustment_amount = 0.0
                
                for item in self.revenue_target_adjustment_account:
                        if flt(item.target_amount) < 0.0:
                                frappe.throw(_("Row#{0}: Target Amount cannot be a negative value.").format(item.idx), title="Invalid Value")

                        if flt(item.net_target_amount)  < 0.0:
                                frappe.throw(_("Row#{0}: Final Target Amount cannot be a negative value.").format(item.idx), title="Invalid Value")
                                
                        if frappe.db.get_value("Account", item.account, "root_type") <> "Income":
                                frappe.throw(_("Row#{0}: `{1}` is not an Income GL.").format(item.idx, item.account), title="Invalid GL")

                        if not item.account_code:
                                item.account_code = frappe.db.get_value("Account", item.account, "account_code")

                        if item.revenue_target:
                                if item.cost_center != item.original_cost_center:
                                        frappe.throw(_("Row#{0}: Cost Center cannot be changed for already set targets.").format(item.idx), title="Invalid Operation")

                                if item.account != item.original_account:
                                        frappe.throw(_("Row#{0}: Account cannot be changed for already set targets.").format(item.idx), title="Invalid Operation")

                                if item.account_code != item.account_code:
                                        frappe.throw(_("Row#{0}: Account Code cannot be changed for already set targets.").format(item.idx), title="Invalid Operation")

                                if flt(item.target_amount) != flt(item.original_target_amount):
                                        frappe.throw(_("Row#{0}: Initial Target Amount cannot be changed for already set targets.").format(item.idx), title="Invalid Operation")

                        tot_target_amount     += flt(item.target_amount)
                        tot_adjustment_amount += flt(item.adjustment_amount)

                self.tot_target_amount     = tot_target_amount
                self.tot_adjustment_amount = tot_adjustment_amount
                self.tot_net_target_amount = flt(tot_target_amount) + flt(tot_adjustment_amount)


