# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class JobCardCancellationTool(Document):
	def validate(self):
		for a in self.items:
			if self.job != a.job_card:
				frappe.throw("Job Card entry associated with the Job Card is not same.")

	def on_submit(self):
		frappe.db.sql ("update `tabJob Card Item` set stock_entry = null where parent = '{0}' ".format(self.job))
		for a in self.items:
			frappe.db.sql ("update `tabStock Entry` set job_card = null where name = '{0}'".format(a.stock))

	def on_cancel(self):
		frappe.throw("This document '{0}' cannot be cancelled".format(self.name))

	def get_stock_items(self):
                entry = frappe.db.sql("select name as stock, branch, from_warehouse,purpose, job_card from `tabStock Entry`  where docstatus = 1 and purpose = \'Material Issue\' and job_card = \'"+ str(self.job) +"\'", as_dict=True)
			
                if entry:
                        self.set('items', [])
                        for d in entry:
                                already = False
				if len(self.get("items")) > 0:
					for a in self.items:
						if a.stock == d.stock:
								already = True
				if not already:
					d.which = "Item"
					row = self.append('items', {})
					row.update(d)
		else:
                        frappe.msgprint("No stock entries related to the job card found. Entries might not have been submitted?")

