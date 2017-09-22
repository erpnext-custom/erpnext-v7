# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# project_invoice.py
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SHIV		 2017/09/21                            Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, time_diff_in_hours, get_datetime, getdate, cint, get_datetime_str

class MBEntry(Document):
	def validate(self):
                self.set_status()
                self.default_validations()
                
        def on_submit(self):
                self.update_boq()

        def before_cancel(self):
                self.set_status()

        def on_cancel(self):
                self.update_boq()
                
        def set_status(self):
                self.status = {
                        "0": "Draft",
                        "1": "Uninvoiced",
                        "2": "Cancelled"
                }[str(self.docstatus or 0)]
                
        def default_validations(self):
                for rec in self.mb_entry_boq:
                        if flt(rec.entry_quantity) > flt(rec.act_quantity):
                                frappe.throw(_("Row{0}: Entry Quantity cannot be greater than Balance Quantity").format(rec.idx))
                        elif flt(rec.entry_amount) > flt(rec.act_amount):
                                frappe.throw(_("Row{0}: Entry Amount cannot be greater than Balance Amount").format(rec.idx))
                        elif flt(rec.entry_quantity) < 0 or flt(rec.entry_amount) < 0:
                                frappe.throw(_("Row{0}: Value cannot be in negative.").format(rec.idx))
        
        def update_boq(self):
                # Updating balance in `tabBOQ Item`
                gtot_entry_amount = 0
                
                for item in self.mb_entry_boq:                        
                        if flt(item.entry_amount) > 0 and item.is_selected:
                                tot_entry_quantity = 0
                                tot_entry_amount   = 0

                                #frappe.msgprint(_("Docstatus: {0}").format(self.docstatus))
                                
                                bi = frappe.db.sql("""
                                                select
                                                        sum(ifnull(entry_quantity,0)) as tot_entry_quantity,
                                                        sum(ifnull(entry_amount,0)) as tot_entry_amount
                                                from `tabMB Entry BOQ`
                                                where boq_item_name = %s
                                                and   name <> %s
                                                and   docstatus = 1
                                                and   is_selected = 1
                                        """, (item.boq_item_name, item.name), as_dict=1)[0]

                                tot_entry_quantity = flt(bi.tot_entry_quantity) + flt(item.entry_quantity)
                                tot_entry_amount   = flt(bi.tot_entry_amount) + flt(item.entry_amount)
                                gtot_entry_amount += flt(item.entry_amount)

                                #frappe.msgprint(_("tot_entry_quantity: {0}").format(tot_entry_quantity))
                                
                                if tot_entry_amount:
                                        if self.docstatus < 2:
                                                base_item = frappe.get_doc("BOQ Item", item.boq_item_name)
                                                base_item.db_set('booked_quantity',flt(tot_entry_quantity))
                                                base_item.db_set('booked_amount',flt(tot_entry_amount))
                                                if self.boq_type == "Milestone Based":
                                                        base_item.db_set('balance_amount',flt(base_item.amount)-flt(base_item.claimed_amount)-flt(tot_entry_amount)-flt(base_item.received_amount))
                                                else:
                                                        base_item.db_set('balance_quantity',flt(base_item.quantity)-flt(base_item.claimed_quantity)-flt(tot_entry_quantity)-flt(base_item.received_quantity))
                                                        base_item.db_set('balance_amount',flt(base_item.amount)-flt(base_item.claimed_amount)-flt(tot_entry_amount)-flt(base_item.received_amount))
                                        else:
                                                base_item = frappe.get_doc("BOQ Item", item.boq_item_name)
                                                base_item.db_set('booked_quantity',flt(bi.tot_entry_quantity))
                                                base_item.db_set('booked_amount',flt(bi.tot_entry_amount))
                                                if self.boq_type == "Milestone Based":
                                                        base_item.db_set('balance_amount',flt(base_item.amount)-flt(base_item.claimed_amount)-flt(bi.tot_entry_amount))
                                                else:
                                                        base_item.db_set('balance_quantity',flt(base_item.quantity)-flt(base_item.claimed_quantity)-flt(bi.tot_entry_quantity))
                                                        base_item.db_set('balance_amount',flt(base_item.amount)-flt(base_item.claimed_amount)-flt(bi.tot_entry_amount))
                                        
