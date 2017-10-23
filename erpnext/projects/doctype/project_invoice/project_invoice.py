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
                self.load_invoice_boq()
                self.set_defaults()
                
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

        def set_defaults(self):
                if self.project:
                        base_project          = frappe.get_doc("Project", self.project)
                        self.company          = base_project.company
                        self.customer         = base_project.customer
                        
                if self.boq:
                        base_boq              = frappe.get_doc("BOQ", self.boq)
                        self.cost_center      = base_boq.cost_center
                        self.branch           = base_boq.branch
                        self.boq_type         = base_boq.boq_type

        # This function is create for "MB Based Invoice" where the BOQ Items are actually
        def load_invoice_boq(self):
                if self.invoice_type == "MB Based Invoice":
                        mb_list = ",".join(["'" + i.entry_name + "'" if i.is_selected == 1 else "'x'" for i in self.project_invoice_mb])
                        
                        mb_boq = frappe.db.sql("""
                                        select boq_item_name, item, uom,
                                                max(ifnull(is_group,0))          as is_group,
                                                max(ifnull(is_selected,0))       as is_selected,
                                                sum(ifnull(idx,0))               as idx,
                                                sum(ifnull(a.original_quantity,0)) as original_quantity,
                                                max(ifnull(original_rate,0))     as original_rate,
                                                sum(ifnull(original_amount,0))   as original_amount,
                                                sum(ifnull(entry_quantity,0))    as entry_quantity,
                                                max(ifnull(entry_rate,0))        as entry_rate,
                                                sum(ifnull(entry_amount,0))      as entry_amount,
                                                max(creation)                    as creation
                                        from (
                                                select
                                                        bi.name as boq_item_name, bi.item, bi.uom,
                                                        bi.is_group,
                                                        0                 as is_selected,
                                                        bi.idx,
                                                        bi.quantity       as original_quantity,
                                                        bi.rate           as original_rate,
                                                        bi.amount         as original_amount,
                                                        0                 as entry_quantity,
                                                        0                 as entry_rate,
                                                        0                 as entry_amount,
                                                        creation
                                                from `tabBOQ Item` as bi
                                                where parent = '{0}'
                                                union all
                                                select
                                                        mb.boq_item_name, mb.item, mb.uom,
                                                        0 as is_group,
                                                        mb.is_selected,
                                                        0 as idx,
                                                        0                 as original_quantity,
                                                        0                 as original_rate,
                                                        0                 as original_amount,
                                                        mb.entry_quantity as entry_quantity,
                                                        mb.entry_rate     as entry_rate,
                                                        mb.entry_amount   as entry_amount,
                                                        creation
                                                from `tabMB Entry BOQ` as mb
                                                where parent in ({1})
                                                and   is_selected = 1
                                        ) as a
                                        group by boq_item_name, item, uom
                                        order by idx
                                        """.format(self.boq, mb_list), as_dict=1)

                        #frappe.msgprint(_("{0}").format(mb_boq))
                        
                        self.project_invoice_boq = []
                        for item in mb_boq:
                                act_quantity = flt(item.original_quantity)
                                act_rate     = flt(item.original_rate)
                                act_amount   = flt(item.original_amount)

                                uptodate_quantity = 0.0
                                uptodate_rate     = 0.0
                                uptodate_amount   = 0.0
                                                
                                if flt(item.entry_amount) > 0:
                                        # Total Invoiced so far (excluding this Invoice)
                                        ti = frappe.db.sql("""
                                                        select
                                                                sum(ifnull(invoice_quantity,0)) as tot_invoice_quantity,
                                                                max(ifnull(invoice_rate,0))     as tot_invoice_rate,
                                                                sum(ifnull(invoice_amount,0))   as tot_invoice_amount
                                                        from   `tabProject Invoice BOQ`
                                                        where  boq_item_name    = '{0}'
                                                        and    is_selected      = 1
                                                        and    docstatus        = 1
                                                        and    parent           != '{1}'
                                                        """.format(item.boq_item_name, self.name), as_dict=1)[0]

                                        if ti:
                                                act_quantity = flt(item.original_quantity)-flt(ti.tot_invoice_quantity)
                                                act_rate     = flt(ti.tot_invoice_rate,0)
                                                act_amount   = flt(item.original_amount)-flt(ti.tot_invoice_amount,0)

                                                uptodate_quantity = flt(ti.tot_invoice_quantity)
                                                uptodate_rate     = flt(ti.tot_invoice_rate,0)
                                                uptodate_amount   = flt(ti.tot_invoice_amount,0)

                                self.append("project_invoice_boq",{
                                        "boq_item_name": item.boq_item_name,
                                        "item": item.item,
                                        "uom": item.uom,
                                        "is_selected": item.is_selected,
                                        "original_quantity": item.original_quantity,
                                        "original_rate": item.original_rate,
                                        "original_amount": item.original_amount,
                                        "act_quantity": act_quantity,
                                        "act_rate": act_rate,
                                        "act_amount": act_amount,
                                        "invoice_quantity": item.entry_quantity,
                                        "invoice_rate": item.entry_rate,
                                        "invoice_amount": item.entry_amount,
                                        "uptodate_quantity": uptodate_quantity,
                                        "uptodate_rate": uptodate_rate,
                                        "uptodate_amount": uptodate_amount,
                                        "creation": self.creation,
                                        "modified": self.modified,
                                        "modified_by": self.modified_by,
                                        "owner": self.owner
                                })
                else:
                        #Direct Invoice
                        for item in self.project_invoice_boq:
                                item.uptodate_quantity = 0.0
                                item.uptodate_rate     = 0.0
                                item.uptodate_amount   = 0.0
                                
                                if flt(item.invoice_amount) > 0 and item.is_selected:
                                        # Total Invoiced so far (excluding this Invoice)
                                        ti = frappe.db.sql("""
                                                        select
                                                                sum(ifnull(invoice_quantity,0)) as tot_invoice_quantity,
                                                                max(ifnull(invoice_rate,0))     as tot_invoice_rate,
                                                                sum(ifnull(invoice_amount,0))   as tot_invoice_amount
                                                        from   `tabProject Invoice BOQ`
                                                        where  boq_item_name    = '{0}'
                                                        and    is_selected      = 1
                                                        and    docstatus        = 1
                                                        and    parent           != '{1}'
                                                        """.format(item.boq_item_name, self.name), as_dict=1)[0]

                                        if ti:
                                                item.uptodate_quantity = flt(ti.tot_invoice_quantity)
                                                item.uptodate_rate     = flt(ti.tot_invoice_rate,0)
                                                item.uptodate_amount   = flt(ti.tot_invoice_amount,0)
                        
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
