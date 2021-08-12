# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt,getdate
from datetime import date, timedelta

class CoalRaisingPayment(Document):
	def validate(self):
		self.validate_data()
		self.get_coal_raising_details()
		if self.deduction:
			self.get_coal_raising_details()
			self.adjust_deduction()
		self.cal_total_amount()
		
	def on_submit(self):
		self.post_journal_entry()

	def before_cancel(self):
		cl_status = frappe.db.get_value("Journal Entry", self.claim_journal, "docstatus")
		if flt(cl_status) < 2:
			frappe.throw("You need to cancel the claim journal entry first!")

	def cal_total_amount(self):
		total_production = 0
		total_amount = 0
		grand_total = 0
		total_penalty = 0
		for item in self.items:
			total_production += flt(item.total_quantity)
			total_amount += flt(item.total_amount)
			grand_total += flt(item.grand_total)
			total_penalty += flt(item.total_penalty)

		self.total_production = total_production
		self.total_amount = total_amount
		self.total_cost = flt(total_amount) / flt(total_production)
		self.grand_total = grand_total
		self.total_penalty = total_penalty

	def validate_data(self):
		if self.from_date > self.to_date:
			frappe.throw('From Date cannot be after To Date')

	def get_coal_raising_details(self):
		data = []
		for d in frappe.db.sql("""
			SELECT
				DISTINCT `group`,tire
			FROM `tabProduction` 
			WHERE branch = '{}' 
			AND posting_date 
			BETWEEN '{}' AND '{}' 
			AND docstatus = 1 
			AND (coal_raising_type != '' or coal_raising_type is not null)
			AND (`group` !='' or `group` is not null)
		""".format(self.branch,self.from_date,self.to_date),as_dict=True):
			# frappe.msgprint(str(d))
			if d.group:
				# data += self.get_tire_data_base_on_group(d.group)
				data1 = frappe.db.sql("""
						SELECT coal_raising_type,
							no_of_labours,amount,machine_payable,
							machine_hours,product_qty,grand_amount,penalty_amount
						FROM `tabProduction`
						WHERE branch = '{0}' AND docstatus = 1
						AND posting_date BETWEEN '{1}' AND '{2}'
						AND `group` = '{3}' AND tire = '{4}'
						AND NOT EXISTS (SELECT crp.name,crp.branch FROM `tabCoal Raising Payment` crp
							INNER JOIN `tabCoal Raising Item` cri
							ON crp.name = cri.parent
							WHERE crp.branch = '{0}' AND crp.docstatus = 1
							AND crp.from_date BETWEEN '{1}' AND '{2}'
							AND crp.to_date BETWEEN '{1}' AND '{2}'
							AND cri.group_name = '{3}' AND cri.tire = '{4}')
					""".format(self.branch,self.from_date,self.to_date,d.group,d.tire),as_dict=True)
				if data1:
					data.append(self.calculation(data1,d.group,d.tire))

		if not data:
			frappe.throw("Payment for Groups involved in production within <b>{0}</b> and <b>{1}</b> is already done".format(self.from_date,self.to_date))

		items = self.set('items',[])
		for d in data:
			row = self.append('items',{})
			row.update(d)

	def calculation(self,data,group,tire):
		row = {}
		row['total_amount'] = 0
		row['manual_qty'] = 0
		row['machine_qty'] = 0
		row['machine_sharing_qty'] = 0
		row['machine_payable'] = 0
		row['no_labour'] = 0
		row['total_penalty'] = 0
		row['grand_total'] = 0
		amount = 0
		for d in data:

			if d.coal_raising_type == 'Manual':
				row['no_labour'] += flt(d.no_of_labours)
				row['manual_qty'] += flt(d.product_qty)
				amount += flt(d.amount)
				row['total_penalty'] += flt(d.penalty_amount)
				row['grand_total'] += flt(d.grand_amount)

			elif d.coal_raising_type == 'Machine Sharing':
				row['no_labour'] += flt(d.no_of_labours)
				row['machine_sharing_qty'] += flt(d.product_qty)
				row['machine_payable'] += flt(d.machine_payable)
				amount += flt(d.amount)
				row['total_penalty'] += flt(d.penalty_amount)
				row['grand_total'] += flt(d.grand_amount)

			elif d.coal_raising_type == 'SMCL Machine':
				row['machine_qty'] += flt(d.product_qty)

		row['total_amount'] += flt(amount)
		row['group_name'] = group
		row['tire'] = tire
		row['total_quantity'] = flt(row['manual_qty']) + flt(row['machine_qty']) + flt(row['machine_sharing_qty'])
		return row

	def adjust_deduction(self):
		for dec in self.deduction:
			for i,item in enumerate(self.items):
				if dec.group == item.group_name:
					self.items[i].total_amount = flt(item.total_amount) - flt(dec.amount)

	def post_journal_entry(self):
		credit_acc,debit_acc,penalty_acc = frappe.db.get_value('Coal Raising Master',self.branch,['account','expense_account','penalty_account'])
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "Coal Raising Payment (" + self.branch + "  " + self.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'Claim payment against : ' + self.name
		je.posting_date = self.posting_date
		je.branch = self.branch

		je.append("accounts", {
				"account": debit_acc,
				"reference_type": "Coal Raising Payment",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"debit_in_account_currency": flt(self.grand_total),
				"debit": flt(self.grand_total)
			})

		je.append("accounts", {
				"account": credit_acc,
				# "party_type": "Employee",
				# "party": self.employee,
				"reference_type": "Coal Raising Payment",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_amount),
				"credit": flt(self.total_amount)
			})
		if self.total_penalty:
			je.append("accounts", {
				"account": penalty_acc,
				"reference_type": "Coal Raising Payment",
				"reference_name": self.name,
				"cost_center": self.cost_center,
				"credit_in_account_currency": flt(self.total_penalty),
				"credit": flt(self.total_penalty),
			})

		je.insert()
		#Set a reference to the claim journal entry
		self.db_set("claim_journal",je.name)
