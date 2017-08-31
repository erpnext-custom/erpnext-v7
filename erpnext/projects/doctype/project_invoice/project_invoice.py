# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		 2017/08/23                            Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, time_diff_in_hours, get_datetime, getdate, cint, get_datetime_str

class ProjectInvoice(Document):
	def validate(self):
                self.default_validations()
                
        def on_submit(self):
                self.update_boq()
                
        def default_validations(self):
                for rec in self.project_invoice_boq:
                        if flt(rec.invoice_quantity) > flt(rec.act_quantity):
                                frappe.throw(_("Row{0}: Invoice Quantity cannot be greater than Balance Quantity").format(rec.idx))
                        elif flt(rec.invoice_amount) > flt(rec.act_amount):
                                frappe.throw(_("Row{0}: Invoice Amount cannot be greater than Balance Amount").format(rec.idx))
                        elif flt(rec.invoice_quantity) < 0 or flt(rec.invoice_amount) < 0:
                                frappe.throw(_("Row{0}: Value cannot be in negative.").format(rec.idx))

        def update_boq(self):
                # Updating balance in `tabBOQ Item`
                gtot_invoice_amount = 0
                
                for item in self.project_invoice_boq:                        
                        if flt(item.invoice_amount) > 0 and item.is_selected:
                                tot_invoice_quantity = 0
                                tot_invoice_amount   = 0
                                
                                bi = frappe.db.sql("""
                                        select sum(ifnull(invoice_quantity,0)) as tot_invoice_quantity,
                                                sum(ifnull(invoice_amount,0)) as tot_invoice_amount
                                        from `tabProject Invoice BOQ`
                                        where boq_item_name = %s
                                        and name <> %s
                                        and docstatus = 1
                                        and is_selected = 1
                                        """, (item.boq_item_name, item.name), as_dict=1)[0]

                                tot_invoice_quantity = flt(bi.tot_invoice_quantity) + flt(item.invoice_quantity)
                                tot_invoice_amount   = flt(bi.tot_invoice_amount) + flt(item.invoice_amount)
                                gtot_invoice_amount += flt(item.invoice_amount)
                                        
                                if tot_invoice_amount:
                                        base_item = frappe.get_doc("BOQ Item", item.boq_item_name)
                                        base_item.db_set('claimed_quantity',flt(tot_invoice_quantity))
                                        base_item.db_set('claimed_amount',flt(tot_invoice_amount))
                                        if self.boq_type == "Milestone Based":
                                                base_item.db_set('balance_amount',flt(base_item.amount)-flt(tot_invoice_amount)-flt(base_item.received_amount))
                                        else:
                                                base_item.db_set('balance_quantity',flt(base_item.quantity)-flt(tot_invoice_quantity)-flt(base_item.received_quantity))
                                                base_item.db_set('balance_amount',flt(base_item.amount)-flt(tot_invoice_amount)-flt(base_item.received_amount))                                                
                                        
                # Updating balance in `tabBOQ`
                if gtot_invoice_amount:
                        bm = frappe.db.sql("""
                                select sum(ifnull(claimed_amount,0)) as tot_claimed_amount
                                from `tabBOQ Item`
                                where parent = %s
                                """, (self.boq), as_dict=1)[0]

                        pi = frappe.db.sql("""
                                select sum(ifnull(price_adjustment_amount,0)) as tot_price_adjustment_amount,
                                        sum(ifnull(total_received_amount,0)) as tot_received_amount
                                from `tabProject Invoice`
                                where boq = %s
                                and docstatus = 1
                                and name <> %s
                                """, (self.boq, self.name), as_dict=1)[0]
                        
                        base_boq = frappe.get_doc("BOQ", self.boq)
                        base_boq.db_set('claimed_amount', flt(bm.tot_claimed_amount)+(flt(pi.tot_price_adjustment_amount)+flt(self.price_adjustment_amount)))
                        base_boq.db_set('received_amount', flt(pi.tot_received_amount)+flt(self.total_received_amount))
                        base_boq.db_set('price_adjustment', flt(pi.tot_price_adjustment_amount)+flt(self.price_adjustment_amount))
                        base_boq.db_set('balance_amount', flt(base_boq.total_amount)+(flt(pi.tot_price_adjustment_amount)+flt(self.price_adjustment_amount))-(flt(pi.tot_received_amount)+flt(self.total_received_amount)))
