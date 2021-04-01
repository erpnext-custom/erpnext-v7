# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint
from frappe.model.document import Document
from frappe.utils import flt, cint, nowdate, getdate, formatdate
from erpnext.accounts.utils import get_fiscal_year
from erpnext.hr.doctype.leave_application.leave_application \
        import get_leave_allocation_records, get_leave_balance_on, get_approved_leaves_for_period
from frappe.utils import getdate, get_first_day, get_last_day, flt

class MergeCLToEL(Document):
	def validate(self):
		self.validate_duplicate()
		self.get_data()

	def validate_duplicate(self):
		current_fiscal_year = get_fiscal_year(getdate(nowdate()), company=self.company)[0]
		if self.fiscal_year == current_fiscal_year:
			frappe.throw("You are not allowed to merge CL balance from current Fiscal year {} to EL".format(current_fiscal_year))
		query = """select name from `tabMerge CL To EL` where docstatus != 2 and fiscal_year = '{0}' and name != '{1}'
			""".format(self.fiscal_year, self.name)
		if self.branch:
			query += " and branch = '{0}'".format(self.branch)
		doc = frappe.db.sql(query)
		if doc:
			frappe.throw("Can not create multiple Entries for the same year")


	def get_data(self):
		fy_start_end_date = frappe.db.get_value("Fiscal Year", self.fiscal_year, ["year_start_date", "year_end_date"])
		if not fy_start_end_date:
			frappe.throw(_("Fiscal Year {0} not found.").format(self.fiscal_year))
	
		from_date = get_first_day(getdate(fy_start_end_date[0]))
		to_date = get_last_day(getdate(fy_start_end_date[1]))
		employee = ''
		allocation_records_based_on_to_date = get_leave_allocation_records(to_date)

		# Edited it out by phuntsho norbu since it selects probationary employes as well. 
		# filters_dict = { "status": "Active", "company": self.company }
		# frappe.msgprint("fitlers: '{}'".format(filters_dict))
		# if self.branch:
		# 	filters_dict['branch'] = self.branch
		# active_employees = frappe.get_all("Employee",
		# 	filters = filters_dict,
		# 	fields = ["name", "employee_name", "department", "branch", "date_of_joining"])
		
		# Changed by Phuntsho on Jan 8 2021. Shouldn't select employees on probation
		condition ="status = 'Active' and company='{company}' and employment_type != 'Probation'".format(company=self.company) 
		if self.branch:
			condition += "and branch = '{}'".format(self.branch)
		active_employees = frappe.db.sql("""select name, employee_name, department, branch, date_of_joining from `tabEmployee` where {cond} """.format(cond=condition), as_dict=True)
		

		
		self.set('items', [])
		for employee in active_employees:
			#leaves allocated
			leaves_allocated = 0.0
			allocation   = get_leave_allocation_records(to_date, employee.name).get(employee.name, frappe._dict()).get(self.leave_type, frappe._dict())
			
			if allocation:
				leaves_allocated = allocation['total_leaves_allocated']
				
			# leaves taken
			leaves_taken = get_approved_leaves_for_period(employee.name, self.leave_type,
				from_date, to_date)

			# closing balance
			'''leave_balance = get_leave_balance_on(employee.name, self.leave_type, to_date,
				allocation_records_based_on_to_date.get(employee.name, frappe._dict()))'''
			employee_id = employee.name
			employee_name = employee.employee_name
			leave_balance = flt(leaves_allocated) - flt(leaves_taken)
			if leave_balance > 0:
				row = self.append('items', {})
				d = {'employee': employee_id, 'employee_name': employee_name,\
					'leaves_allocated': leaves_allocated, 'leaves_taken': leaves_taken, 'leave_balance': leave_balance}
				row.update(d)


	def on_submit(self):
		for em in self.items:
			leave_allocation_id = ""
			for a in frappe.db.sql("""
					select name from `tabLeave Allocation` 
					where employee = '{0}' 
					and leave_type = 'Earned Leave' 
					and docstatus = 1 
					order by to_date desc limit 1""".format(em.employee), as_dict=True):
				leave_allocation_id = a.name
			if not leave_allocation_id:
				frappe.throw("No Leave Allocation found for employee {}".format(em.employee_name))

			frappe.db.sql("""
					update `tabLeave Allocation` set cl_balance = {0}, cf_reference = '{1}',
					total_leaves_allocated = total_leaves_allocated + {0} 
					where name  = '{2}'
					""".format(em.leave_balance, em.parent, leave_allocation_id))

	def on_cancel(self):
		for em in self.get('items'):
			frappe.db.sql("""
					UPDATE 
						`tabLeave Allocation` 
					SET 
						cl_balance = 0, 
						cf_reference = '',
						total_leaves_allocated = total_leaves_allocated - {0} 
					WHERE 
						docstatus = 1 and
						employee = '{1}' and
						cf_reference = '{2}'
					""".format(em.leave_balance, em.employee, em.parent))
		frappe.msgprint(" Updated Leave Allocation Record ")