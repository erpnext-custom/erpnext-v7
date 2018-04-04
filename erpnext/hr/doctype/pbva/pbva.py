# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, date_diff, cint
from erpnext.hr.doctype.salary_structure.salary_structure import get_salary_tax

class PBVA(Document):
	def validate(self):
		#self.validate_duplicate()
		self.calculate_values()

	def on_submit(self):
		cc_amount = {}
		for a in self.items:
			tax = get_salary_tax(a.amount)
			cc = frappe.db.get_value("Employee", a.employee, "cost_center")
			if cc_amount.has_key(cc):
				cc_amount[cc]['amount'] = cc_amount[cc]['amount'] + a.amount
				cc_amount[cc]['tax'] = cc_amount[cc]['tax'] + a.tax_amount
				cc_amount[cc]['balance_amount'] = cc_amount[cc]['balance_amount'] + a.balance_amount
			else:
				row = {"amount": a.amount, "tax": a.tax_amount, "balance_amount":a.balance_amount}
				cc_amount[cc] = row;

		self.post_journal_entry(cc_amount)

	def validate_duplicate(self):
		doc = frappe.db.sql("select name from tabPBVA where docstatus != 2 and fiscal_year = \'"+str(self.fiscal_year)+"\' and name != \'"+str(self.name)+"\'")		
		if doc:
			frappe.throw("Can not create multiple PBVA for the same year")

	def calculate_values(self):
		if self.items:
			tot = tax = net = 0
			for a in self.items:
				a.tax_amount = get_salary_tax(a.amount)
				a.balance_amount = flt(a.amount) - flt(a.tax_amount)
				tot += flt(a.amount)
				tax += flt(a.tax_amount)
				net += flt(a.balance_amount)

			self.total_amount = tot
			self.tax_amount   = tax
			self.net_amount   = net
		else:
			frappe.throw("Cannot save without employee details")

	def post_journal_entry(self, cc_amount):
		je = frappe.new_doc("Journal Entry")
		je.flags.ignore_permissions = 1 
		je.title = "PBVA for " + self.branch + "(" + self.name + ")"
		je.voucher_type = 'Bank Entry'
		je.naming_series = 'Bank Payment Voucher'
		je.remark = 'PBVA payment against : ' + self.name;
		je.posting_date = self.posting_date
		je.branch = self.branch

		pbva_account = frappe.db.get_single_value("HR Accounts Settings", "pbva_account")
		tax_account = frappe.db.get_single_value("HR Accounts Settings", "salary_tax_account")
		expense_bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		if not pbva_account:
			frappe.throw("Setup PBVA Account in HR Accounts Settings")
		if not tax_account:
			frappe.throw("Setup Salary Tax Account in HR Accounts Settings")
		if not expense_bank_account:
			frappe.throw("Setup Expense Bank Account for your branch")
		
		for key in cc_amount.keys():
			je.append("accounts", {
					"account": pbva_account,
					"reference_type": "PBVA",
					"reference_name": self.name,
					"cost_center": key,
					"debit_in_account_currency": flt(cc_amount[key]['amount']),
					"debit": flt(cc_amount[key]['amount']),
				})
		
			je.append("accounts", {
					"account": expense_bank_account,
					"cost_center": key,
					"credit_in_account_currency": flt(cc_amount[key]['balance_amount']),
					"credit": flt(cc_amount[key]['balance_amount']),
				})
			
			je.append("accounts", {
					"account": tax_account,
					"cost_center": key,
					"credit_in_account_currency": flt(cc_amount[key]['tax']),
					"credit": flt(cc_amount[key]['tax']),
				})

		je.insert()

		self.db_set("journal_entry", je.name)

	def on_cancel(self):
		jv = frappe.db.get_value("Journal Entry", self.journal_entry, "docstatus")
		if jv != 2:
			frappe.throw("Can not cancel PBVA without canceling the corresponding journal entry " + str(self.journal_entry))
		else:
			self.db_set("journal_entry", "")


	#@frappe.whitelist()
	def get_pbva_details(self):
                if not self.fiscal_year:
			frappe.throw("Fiscal Year is Mandatory")

		#start, end = frappe.db.get_value("Fiscal Year", self.fiscal_year, ["year_start_date", "year_end_date"])
                start = str(self.fiscal_year)+'-01-01'
		end   = str(self.fiscal_year)+'-12-31'
		
		query = """
                                select
                                        e.name as employee,
                                        e.employee_name,
                                        e.employment_type,
                                        e.branch,
                                        e.date_of_joining,
                                        e.relieving_date,
                                        e.reason_for_resignation as leaving_type,
					e.salary_mode,
					e.bank_name,
					e.bank_ac_no,
                                        datediff(least(ifnull(e.relieving_date,'9999-12-31'),'{2}'),
                                                        greatest(e.date_of_joining,'{1}'))+1 days_worked,
                                        (
                                                select
                                                        sd.amount
                                                from
                                                        `tabSalary Detail` sd,
                                                        `tabSalary Slip` sl,
                                                        `tabSalary Structure` ss
                                                where sd.parent = sl.name
                                                and sl.employee = e.name
                                                and sl.salary_structure = ss.name
                                                and sd.salary_component = 'Basic Pay'
                                                and sl.actual_basic = 0
                                                and sl.docstatus = 1
                                                and ss.eligible_for_pbva = 1
                                                and sl.fiscal_year <= {0}
                                                order by sl.month desc limit 1
                                        ) as basic_pay
                                from tabEmployee e
                                where (
                                        ('{3}' = 'Active' and e.date_of_joining <= '{2}' and ifnull(e.relieving_date,'9999-12-31') > '{2}')
                                        or
                                        ('{3}' = 'Left' and ifnull(e.relieving_date,'9999-12-31') between '{1}' and '{2}')
                                        or
                                        ('{3}' = 'All' and e.date_of_joining <= '{2}' and ifnull(e.relieving_date,'9999-12-31') >= '{1}')
                                        )
                                and not exists(
                                                select 1
                                                from `tabPBVA Details` bd, `tabPBVA` b
                                                where b.fiscal_year = '{0}'
                                                and b.name <> '{4}'
                                                and bd.parent = b.name
                                                and bd.employee = e.employee
                                                and b.docstatus in (0,1))
                                order by e.branch
                        """.format(self.fiscal_year, start, end, self.employee_status, self.name)
		
		entries = frappe.db.sql(query, as_dict=True)
		self.set('items', [])

		start = getdate(start)
		end = getdate(end)

		for d in entries:
                        '''
			joining = getdate(d.date_of_joining)
			relieving = getdate(d.relieving_date)

			if not (joining >= start and joining <= end): 
				d.date_of_joining = None
			if not (relieving >= start and relieving <= end): 
				d.relieving_date = None

			d.days_worked = date_diff(getdate(self.fiscal_year + '-12-31'), getdate(self.fiscal_year + '-01-01'))
			if d.date_of_joining: 
				d.days_worked = date_diff(getdate(self.fiscal_year + '-12-31'), d.date_of_joining)

			if d.relieving_date:
				d.days_worked = date_diff(d.relieving_date, getdate(self.fiscal_year + '-01-01'))
	
			if d.relieving_date and d.date_of_joining:
                                d.days_worked = date_diff(d.relieving_date, d.date_of_joining)

			d.days_worked = cint(d.days_worked) + 1
			'''
			d.amount = 0
			row = self.append('items', {})
			row.update(d)

@frappe.whitelist()
def get_pbva_percent(employee):
	group = frappe.db.get_value("Employee", employee, "employee_group")
	if group in ("Chief Executive Officer", "Executive"):
		return "above"
	else:
		return "below"
