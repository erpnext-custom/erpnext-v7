# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TechnicalSanction(Document):
	def validate(self):
		self.update_maf()
		if self.outsource:
			if not self.supplier:
				frappe.throw("A Contractor must be selected as the work type is outsource")

	def on_submit(self):
		pass

	def update_maf(self):
		if self.docstatus == 2:
			frappe.db.sql("update `tabMaintenance Application Form` set technical_sanction = NULL where name ='{1}'".format(self.name, self.maf))
		else:
			if self.maf and self.name:
				frappe.db.sql("update `tabMaintenance Application Form` set technical_sanction = '{0}' where name ='{1}'".format(self.name, self.maf))
			else:
				frappe.throw("Not able to update MAF")


	def get_technical_sanction_items(self):
		items = frappe.db.sql("select se.name as stock_entry, sed.name as stock_entry_detail, sed.item_code as item, sed.item_name as item_name, sed.stock_uom as uom, sed.qty as quantity, sed.amount from `tabStock Entry Detail` sed, `tabStock Entry` se where se.docstatus = 1 and sed.parent = se.name and se.purpose = 'Material Issue' and se.technical_sanction = \'"+ str(self.name) +"\'", as_dict=True)

		if items:
			for d in items:
				if self.material_items:
					for a in self.material_items:
						if a.stock_entry != d.stock_entry and d.stock_entry_detail != a.stock_entry_detail:
							frappe.msgprint("{0}".format(a))
							row = self.append('material_items', {})
							row.update(d)	
				else:
					row = self.append('material_items', {})
					row.update(d)	
		else:
			frappe.msgprint("No stock entries related to the Technical Sanction found. Entries might not have been submitted?")
