# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, date_diff, nowdate
from frappe.utils.data import get_first_day, get_last_day, add_days
from erpnext.custom_utils import check_future_date
from erpnext.accounts.general_ledger import make_gl_entries
from erpnext.controllers.accounts_controller import AccountsController

class TeaAllowance(AccountsController):
	def validate(self):
		check_future_date(self.start_date)
		check_future_date(self.end_date)
		self.company = frappe.db.get_single_value('Global Defaults', 'default_company')

		tea_amount = 0.0
		for i in self.items:
			tea_amount += flt(i.eligible_days) * flt(self.allowance_amount)
		if tea_amount != self.total_amount:
			frappe.msgprint("Tea Allowance amount doesn't match {0} and {1}".format(tea_amount, self.total_amount))  	

	def on_submit(self):
		self.post_gl_entry()

	def on_cancel(self):
		self.post_gl_entry()

	def get_details(self):
		self.set('items', [])
		qry = """
			select
			name, employee_name, designation 
			from `tabEmployee` e
			where status = 'Active'
			order by name
		"""
		
		#Total Days in month	
		total_days_in_month = date_diff(self.end_date, self.start_date) + 1

		#Get Total Holiday from Holiday List
		for a in frappe.db.sql("select count(*) as total_holiday from `tabHoliday` where holiday_date between '{0}' and '{1}'".format(self.start_date, self.end_date), as_dict=1):
			total_holiday = a.total_holiday

		total_amount = 0.0		
		for e in frappe.db.sql(qry, as_dict=True):
			for b in frappe.db.sql("select count(*) as not_eligible_days from `tabAttendance` where att_date between '{0}' and '{1}' and employee = '{2}' and status in ('Tour','Half Day','Absent','Leave')".format(self.start_date, self.end_date, e.name), as_dict=1):
				not_eligible_days = b.not_eligible_days
			
			total_eligible_days = total_days_in_month - (total_holiday + not_eligible_days)
			if total_eligible_days < 0:
				total_eligible_days = 0.00

			e.employee = e.name
			e.eligible_days = flt(total_eligible_days)
			e.tea_allowance = flt(total_eligible_days) * flt(self.allowance_amount)
			row = self.append('items', {})
			row.update(e)
			total_amount_s = flt(total_eligible_days) * flt(self.allowance_amount)
			total_amount += total_amount_s

		self.db_set("total_amount", total_amount)

	def post_gl_entry(self):
                gl_entries = []
                credit_account = frappe.db.get_single_value("HR Accounts Settings", "other_allowance")
                debit_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
                gl_entries.append(
                        self.get_gl_dict({
                            "account": debit_account,
                            "debit": self.total_amount,
                            "debit_in_account_currency": self.total_amount,
                            "voucher_no": self.name,
                            "voucher_type": "Tea Allowance",
                            "cost_center": self.cost_center,
                            "company": self.company,
			    "business_activity": self.business_activity,	
                        })
                  )
                gl_entries.append(
                        self.get_gl_dict({
                                "account": credit_account,
                                "credit": self.total_amount,
                                "credit_in_account_currency": self.total_amount,
                                "voucher_no": self.name,
                                "voucher_type": "Tea Allowance",
                                "cost_center": self.cost_center,
                                "company": self.company,
				"business_activity": self.business_activity,
                        })
                    )

                make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
