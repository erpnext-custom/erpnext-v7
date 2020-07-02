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

class AllowancePayment(AccountsController):
	def validate(self):
		check_future_date(self.start_date)
		check_future_date(self.end_date)
		self.company = frappe.db.get_single_value('Global Defaults', 'default_company')
		self.validate_account()
		self.validate_amount()

	def validate_account(self):
		if self.allowance_type == "Tea Allowance":
			self.account = frappe.db.get_single_value("HR Accounts Settings", "tea_allowance")
		else:
			self.account = frappe.db.get_single_value("HR Accounts Settings", "health_and_safety_allowance")
		
		if self.branch:
			self.bank_account = frappe.db.get_value("Branch", self.branch, "expense_bank_account")
		
		if not self.account and not self.bank_account:
			frappe.throw("Allowance account is not mapped in HR Accounts Settings or Bank Account for selected branch is not Mapped")
	
	def validate_amount(self):
		amount = 0.0
		for i in self.items:
			amount += flt(i.eligible_days) * flt(self.allowance_rate) + flt(i.eligible_half_days * (self.allowance_rate/2))

		if amount != self.total_amount:
			frappe.msgprint("Allowance amount doesn't match {0} and {1}".format(amount, self.total_amount))

	def on_submit(self):
		self.post_gl_entry()

	def on_cancel(self):
		self.post_gl_entry()

	def get_details(self):
		self.set('items', [])
		if self.allowance_type == "Tea Allowance":
			qry = """
				select
				name, employee_name, designation 
				from `tabEmployee` e
				where e.status = 'Active'
				order by name
			"""
		else:
			qry = """
				select 
				employee as name, employee_name, designation
				from `tabHSA Employee` e
				where e.eligible = 1
				order by employee 
			"""
		#Total Days in month    
		total_days_in_month = date_diff(self.end_date, self.start_date) + 1
		#Get Total Holiday from Holiday List
		for a in frappe.db.sql("select count(*) as total_holiday from `tabHoliday` where holiday_date between '{0}' and '{1}'".format(self.start_date, self.end_date), as_dict=1):
			total_holiday = a.total_holiday
		
		total_amount = 0.0
		for e in frappe.db.sql(qry, as_dict=True):
			if self.allowance_type == "Tea Allowance":
				for b in frappe.db.sql("select count(*) as not_eligible_days from `tabAttendance` where att_date between '{0}' and '{1}' and employee = '{2}' and status in ('Tour','Half Day','Absent','Leave') and att_date not in (select holiday_date from `tabHoliday` where holiday_date between '{0}' and '{1}')".format(self.start_date, self.end_date, e.name), as_dict=1):
					not_eligible_days = b.not_eligible_days

				total_eligible_days = total_days_in_month - (total_holiday + not_eligible_days)
				total_eligible_half_days = 0
			else:
				date_list, total_saturday = self.get_weekly_off_date_list()
				absent_saturday = 0
				not_eligible_days = 0
				for a in frappe.db.sql("select att_date from `tabAttendance` where att_date between '{0}' and '{1}' and employee = '{2}' and status in ('Tour','Absent','Leave')".format(self.start_date, self.end_date, e.name), as_dict=1):
					if a.att_date in date_list:
						absent_saturday +=1
					not_eligible_days +=1 
				eligible_saturday = flt(total_saturday) - flt(absent_saturday)
				half_day_leave = 0
				for d in frappe.db.sql("select count(*) as half_day_leave from `tabAttendance` where att_date between '{0}' and '{1}' and employee = '{2}' and status = 'Half Day'".format(self.start_date, self.end_date, e.name), as_dict=1):
					half_day_leave = d.half_day_leave
		
				total_eligible_days = total_days_in_month - (total_holiday + not_eligible_days + half_day_leave + eligible_saturday)
				
				total_eligible_half_days = eligible_saturday + half_day_leave

			e.employee = e.name

			e.eligible_days = flt(total_eligible_days)
			e.eligible_half_days = flt(total_eligible_half_days)
			allowance_amount = flt(total_eligible_days) * flt(self.allowance_rate) + (flt(total_eligible_half_days) * (flt(self.allowance_rate)/2))
			e.allowance_amount = allowance_amount
			row = self.append('items', {})
			row.update(e)
			total_amount += allowance_amount

		self.db_set("total_amount", total_amount)

	def get_weekly_off_date_list(self):
		start_date, end_date = getdate(self.start_date), getdate(self.end_date)

		from dateutil import relativedelta
		from datetime import timedelta
		import calendar

		date_list = []
		existing_date_list = []
		day = "Saturday"
		weekday = getattr(calendar, (day).upper())
		reference_date = start_date + relativedelta.relativedelta(weekday=weekday)
		existing_date_list = [getdate(holiday.holiday_date) for holiday in frappe.db.sql("""
												select holiday_date 
												from `tabHoliday` h, `tabHoliday List` l 
												where h.parent = l.name 
												and '{0}' between l.from_date and l.to_date 
												and '{1}' between l.from_date and l.to_date 
												""".format(start_date, end_date), as_dict=True)]

		#existing_date_list = [getdate(holiday.holiday_date) for holiday in self.get("holidays")]
		saturday_count = 0 
		while reference_date <= end_date:
			if reference_date not in existing_date_list:
				date_list.append(reference_date)
				saturday_count += 1
			reference_date += timedelta(days=7)
		return date_list, saturday_count


	def post_gl_entry(self):
		gl_entries = []
		debit_account = self.account
		credit_account = self.bank_account 
		gl_entries.append(
			self.get_gl_dict({
			    "account": debit_account,
			    "debit": self.total_amount,
			    "debit_in_account_currency": self.total_amount,
			    "voucher_no": self.name,
			    "voucher_type": "Allowance Payment",
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
				"voucher_type": "Allowance Payment",
				"cost_center": self.cost_center,
				"company": self.company,
				"business_activity": self.business_activity,
			})
		    )

		make_gl_entries(gl_entries, cancel=(self.docstatus == 2),update_outstanding="No", merge_entries=False)
