# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import utils
from frappe.utils import flt, getdate
from erpnext.custom_utils import check_future_date
from frappe.model.document import Document

class ItemRegisterTool(Document):
	def validate(self):
                check_future_date(self.posting_date)
                self.validate_data()
                #self.check_balance()

        def on_submit(self):
                self.update_stock_register()
 		#self.check_balance()
	def on_update(self):
		self.check_balance()

        def on_cancel(self):
                self.delete_entries()

        def validate_data(self):
                if not self.purpose:
                        frappe.throw("Purpose is Mendatory")
                if self.purpose == 'Transfer' and not self.to_employee:
                        frappe.throw("Transfer To Is Mandiatory")
                if not self.items:
                        frappe.throw("No Items Selected for {0}".format(self.purpose))

		if self.branch != frappe.db.get_value("Employee", self.from_employee, "branch"):
                        frappe.throw("Branch Entered and Employee Branch Not Matching")


        def check_balance(self):
                qty_data = frappe.db.sql("select item_code, sum(qty) as qty from `tabItem Register Table` where parent = %s group by item_code", self.name, as_dict=True)
		#frappe.msgprint("{0}".format(qty_data))
                for i in qty_data:
                        branch = frappe.db.get_value("Employee", self.from_employee, "branch")
                        #frappe.msgprint("{0}".format(branch))
                        bal = frappe.db.sql(""" select sum(ifnull(qty,0)) as qty from `tabConsumable Register Entry` 
                                        where issued_to = '{0}' and item_code = '{1}' and docstatus = 1 and branch = '{2}'
                                """.format(self.from_employee, i.item_code, branch), as_dict =1)[0]
                        bal_qty = flt(bal.qty)
                        if bal_qty < flt(i.qty):
                                frappe.throw("Not enough balance To  {0}. The balance of  '{1}' is   {2}".format(self.purpose, i.item_code, bal_qty))


	def update_stock_register(self):
		 for a in self.items:
                        if self.purpose == 'Remove':
                                rem = frappe.new_doc("Consumable Register Entry")
                                rem.flags.ignore_permissions = 1
                                rem.issued_to = self.from_employee
                                rem.branch = frappe.db.get_value("Employee", self.from_employee, "branch")
                                rem.date = self.posting_date
                                rem.qty = -1*a.qty
                                rem.item_code = a.item_code
                                rem.ref_doc = self.name
                                rem.submit()
                        if self.purpose == 'Transfer':
                                sen = frappe.new_doc("Consumable Register Entry")
                                sen.flags.ignore_permissions = 1
                                sen.issued_to = self.from_employee
                                sen.branch = frappe.db.get_value("Employee", self.from_employee, "branch")
                                sen.date = self.posting_date
                                sen.qty = -1*a.qty
                                sen.item_code = a.item_code
                                sen.ref_doc = self.name
                                sen.submit()

                                rec = frappe.new_doc("Consumable Register Entry")
                                rec.flags.ignore_permissions = 1
                                rec.issued_to = self.to_employee
                                rec.branch = frappe.db.get_value("Employee", self.to_employee, "branch")
                                rec.date = self.posting_date
                                rec.qty = 1*a.qty
                                rec.item_code = a.item_code
                                rec.ref_doc = self.name
                                rec.submit()

	def delete_entries(self):
                frappe.db.sql("delete from `tabConsumable Register Entry` where ref_doc = %s", self.name)
		
