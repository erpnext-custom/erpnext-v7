# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# project_invoice.py
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
from erpnext.controllers.accounts_controller import AccountsController

class ProjectInvoice(AccountsController):
	def validate(self):
                self.set_status()
                self.default_validations()
                
        def on_submit(self):
                self.update_boq_item()
                self.update_boq()
                
                if self.invoice_type == "MB Based Invoice":
                        self.update_mb_entries()
                
                self.make_gl_entries()

        def before_cancel(self):
                self.set_status()

        def on_cancel(self):
                self.make_gl_entries()
                
                self.update_boq_item()
                self.update_boq()
                
                if self.invoice_type == "MB Based Invoice":
                        self.update_mb_entries()
                
        def set_status(self):
                self.status = {
                        "0": "Draft",
                        "1": "Unpaid",
                        "2": "Cancelled"
                }[str(self.docstatus or 0)]
                
        def default_validations(self):
                for rec in self.project_invoice_boq:
                        if flt(rec.invoice_quantity) > flt(rec.act_quantity):
                                frappe.throw(_("Row{0}: Invoice Quantity cannot be greater than Balance Quantity").format(rec.idx))
                        elif flt(rec.invoice_amount) > flt(rec.act_amount):
                                frappe.throw(_("Row{0}: Invoice Amount cannot be greater than Balance Amount").format(rec.idx))
                        elif flt(rec.invoice_quantity) < 0 or flt(rec.invoice_amount) < 0:
                                frappe.throw(_("Row{0}: Value cannot be in negative.").format(rec.idx))

        def make_gl_entries(self):
                if self.net_invoice_amount:
                        from erpnext.accounts.general_ledger import make_gl_entries
                        gl_entries = []
                        self.posting_date = self.invoice_date

                        inv_gl = frappe.db.get_value(doctype="Projects Accounts Settings",fieldname="project_invoice_account", as_dict=True)
                        rec_gl = frappe.db.get_value(doctype="Company",filters=self.company,fieldname="default_receivable_account", as_dict=True)

                        if not inv_gl:
                                frappe.throw(_("Project Invoice Account is not defined in Projects Accounts Settings."))

                        if not rec_gl:
                                frappe.throw(_("Default Receivable Account is not defined in Company Settings."))
                        
                        gl_entries.append(
                                self.get_gl_dict({
                                       "account":  rec_gl.default_receivable_account,
                                       "party_type": "Customer",
                                       "party": self.customer,
                                       "against": inv_gl.project_invoice_account,
                                       "debit": self.net_invoice_amount,
                                       "debit_in_account_currency": self.net_invoice_amount,
                                       "against_voucher": self.name,
                                       "against_voucher_type": self.doctype,
                                       "project": self.project,
                                       "cost_center": self.cost_center
                                }, self.currency)
                        )

                        gl_entries.append(
                                self.get_gl_dict({
                                       "account":  inv_gl.project_invoice_account,
                                       "against": self.customer,
                                       "credit": self.net_invoice_amount,
                                       "credit_in_account_currency": self.net_invoice_amount,
                                       "project": self.project,
                                       "cost_center": self.cost_center
                                }, self.currency)
                        )


                        make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)

        def update_boq_item(self):
                if self.invoice_type == "Direct Invoice":
                        # Direct Invoice
                        item_list = frappe.db.sql("""
                                        select
                                                pib.boq_item_name,
                                                sum(
                                                        case
                                                        when '{0}' = 'Milestone Based' then 0
                                                        else
                                                                case
                                                                when pib.docstatus < 2 then ifnull(pib.invoice_quantity,0)
                                                                else -1*ifnull(pib.invoice_quantity,0)
                                                                end
                                                        end
                                                    ) as invoice_quantity,
                                                sum(
                                                        case
                                                        when pib.docstatus < 2 then ifnull(pib.invoice_amount,0)
                                                        else -1*ifnull(pib.invoice_amount,0)
                                                        end
                                                    ) as invoice_amount
                                        from `tabProject Invoice BOQ` pib
                                        where pib.parent         = '{1}'
                                        and   pib.is_selected    = 1
                                        and   pib.invoice_amount > 0
                                        group by pib.boq_item_name
                                        """.format(self.boq_type, self.name), as_dict=1)
                
                        for item in item_list:
                                frappe.db.sql("""
                                        update `tabBOQ Item`
                                        set
                                                claimed_quantity = ifnull(claimed_quantity,0)+ifnull({1},0),
                                                claimed_amount   = ifnull(claimed_amount,0)+ifnull({2},0),
                                                balance_quantity = ifnull(balance_quantity,0) - ifnull({1},0),
                                                balance_amount   = ifnull(balance_amount,0) - ifnull({2},0)
                                        where name = '{0}'
                                        """.format(item.boq_item_name, flt(item.invoice_quantity), flt(item.invoice_amount)))
                else:
                        # MB Based Invoice
                        boq_list = frappe.db.sql("""
                                        select
                                                meb.boq_item_name,
                                                sum(
                                                        case
                                                        when '{0}' = 'Milestone Based' then 0
                                                        else
                                                                case
                                                                when pim.docstatus < 2 then ifnull(meb.entry_quantity,0)
                                                                else -1*ifnull(meb.entry_quantity,0)
                                                                end
                                                        end
                                                ) as entry_quantity,
                                                sum(
                                                        case
                                                        when pim.docstatus < 2 then ifnull(meb.entry_amount,0)
                                                        else -1*ifnull(meb.entry_amount,0)
                                                        end
                                                ) as entry_amount
                                        from  `tabProject Invoice MB` as pim, `tabMB Entry BOQ` meb
                                        where pim.parent        = '{1}'
                                        and   pim.is_selected   = 1
                                        and   meb.parent        = pim.entry_name
                                        and   meb.is_selected   = 1
                                        group by meb.boq_item_name
                                        """.format(self.boq_type, self.name), as_dict=1)

                        for item in boq_list:
                                frappe.db.sql("""
                                        update `tabBOQ Item`
                                        set
                                                claimed_quantity = ifnull(claimed_quantity,0)+ifnull({1},0),
                                                booked_quantity  = ifnull(booked_quantity,0)-ifnull({1},0),
                                                claimed_amount   = ifnull(claimed_amount,0)+ifnull({2},0),
                                                booked_amount    = ifnull(booked_amount,0)-ifnull({2},0)
                                        where name = '{0}'
                                """.format(item.boq_item_name, flt(item.entry_quantity), flt(item.entry_amount)))
                        
        def update_boq(self):
                # Updating `tabBOQ`
                tot_invoice_amount = flt(self.net_invoice_amount) if self.docstatus < 2 else -1*flt(self.net_invoice_amount)
                tot_price_adj      = flt(self.price_adjustment_amount) if self.docstatus < 2 else -1*flt(self.price_adjustment_amount)

                if tot_invoice_amount or tot_price_adj:
                        base_boq = frappe.get_doc("BOQ", self.boq)
                        base_boq.db_set('claimed_amount', flt(base_boq.claimed_amount)+flt(tot_invoice_amount))
                        base_boq.db_set('price_adjustment', flt(base_boq.price_adjustment)+flt(tot_price_adj))
                        base_boq.db_set('balance_amount', flt(base_boq.balance_amount)+flt(tot_price_adj))

        def update_mb_entries(self):
                # Updating `tabMB Entry`
                for mb in self.project_invoice_mb:
                        if flt(mb.entry_amount) > 0 and mb.is_selected:
                                entry_amount = flt(mb.entry_amount) if self.docstatus < 2 else -1*flt(mb.entry_amount)
                                        
                                frappe.db.sql("""
                                        update `tabMB Entry`
                                        set
                                                total_invoice_amount = ifnull(total_invoice_amount,0) + ifnull({1},0),
                                                total_balance_amount = ifnull(total_balance_amount,0) - ifnull({1},0),
                                                status = (case
                                                                when (ifnull(total_balance_amount,0) - ifnull({1},0)) > 0 then 'Uninvoiced'
                                                                else 'Invoiced'
                                                          end)
                                        where name = '{0}'
                                        """.format(mb.entry_name, flt(entry_amount)))
                                        

@frappe.whitelist()
def get_mb_list(project, boq_name, entry_name):
        if entry_name == "dummy":
                entry_name = None

        if boq_name == "dummy":
                boq_name = None
                
        result = frappe.db.sql("""
                select *
                from `tabMB Entry`
                where project = %s
                and docstatus = 1
                and total_balance_amount > 0
                and boq = ifnull(%s,boq)
                and name = ifnull(%s,name)
                """, (project, boq_name, entry_name), as_dict=True)

        return result
