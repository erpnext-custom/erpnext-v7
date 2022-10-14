# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt,getdate,nowdate,cint,add_days

class ConsolidationAdjustmentEntry(Document):
	def validate(self):
		self.set_missing_value()
  
	def after_insert(self):
		for item in self.items:
			item.adjustment_entry_ref = self.name
   
	def on_submit(self):
		self.valid_total_debit_credit()
		self.append_consolidation_transaction()
  
	def on_cancel(self):
		self.remove_consolidation_transaction()
	def valid_total_debit_credit(self):
		if self.total_credit != self.total_debit:
			frappe.throw('Total debit and credit not equal')
	def remove_consolidation_transaction(self):
		frappe.db.sql('''
                delete from `tabConsolidation Transaction Item` where parent = '{}' and adjustment_entry_ref = '{}'
                '''.format(self.consolidation_transaction,self.name))
	def append_consolidation_transaction(self):
		doc = frappe.get_doc("Consolidation Transaction",self.consolidation_transaction)
		for item in self.items:
			doc.append('items',{
				"account":item.account,
				"account_code":item.account_code,
				"interco":item.interco,
				"opening_debit":item.opening_debit,
				"debit":item.debit,
				"opening_credit":item.opening_credit,
				"credit":item.credit,
				"amount":item.amount,
				"entity":item.entity,
				"time":item.time,
				"flow":item.flow,
				"segment":item.segment,
				"adjustment_entry_ref":item.adjustment_entry_ref,
			})
		doc.save(ignore_permissions=1)

	def set_missing_value(self):
		dhi_setting = frappe.get_doc('DHI Setting')
		year					= getdate(self.to_date).year 
		month 					= getdate(self.to_date).month
		time					= str(year) + str(month) if len(str(month)) == 2 else str(year) + '0' + str(month)
		self.total_debit = self.total_credit = 0
		for item in self.items:
			item.time = time
			item.entity = dhi_setting.entity
			item.flow = dhi_setting.flow
			item.segment = dhi_setting.segment
			item.interco 	= str('I_' + item.company_code)
			self.total_credit += flt(flt(item.credit) + flt(item.opening_credit))
			self.total_debit += flt(flt(item.debit) + flt(item.opening_debit))
			if not item.root_type:
				item.root_type = frappe.db.get_value('DHI GCOA',item.account_code,'root_type')
			if not item.root_type:
				frappe.throw('You need to set root type for GCOA {}'.format(frappe.bold(item.account)))
			item.amount = flt(flt(item.debit) + flt(item.opening_debit)) - flt(flt(item.credit) + flt(item.opening_credit)) if item.root_type in ['Asset','Expense'] else flt(flt(item.debit) + flt(item.opening_debit)) - flt(flt(item.credit) + flt(item.opening_credit))
