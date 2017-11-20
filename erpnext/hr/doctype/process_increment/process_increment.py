# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, nowdate
from frappe import _
from erpnext.hr.doctype.salary_increment.salary_increment import get_employee_payscale
from erpnext.hr.hr_custom_functions import get_month_details

class ProcessIncrement(Document):
        def get_emp_list(self):
		"""
			Returns list of active employees based on selected criteria
			and for which salary structure exists
		"""
		import calendar
		
		cond = self.get_filter_condition()
		cond += self.get_joining_releiving_condition()

                increment_month = calendar.month_name[int(self.month)]
                '''
                increment_month = ''
                if self.month == '01':
                        increment_month = 'January'
                elif self.month == '07':
                        increment_month = 'July'
                else:
                        frappe.throw(_("Increment cycle can only be processed for January/July."))
                '''

		emp_list = frappe.db.sql("""
			select t1.name, t1.employee_subgroup, t1.company, t1.branch,
			t1.department, t1.division, t1.section, t1.employee_name
			from `tabEmployee` t1, `tabSalary Structure` t2
			where t1.docstatus!=2 and t2.docstatus != 2
			and t1.increment_and_promotion_cycle = '%s' and 
			ifnull(t2.salary_slip_based_on_timesheet,0) = 0 and t1.name = t2.employee
		%s """% (increment_month,cond),as_dict=True)

		#frappe.msgprint(str(emp_list))
		return emp_list

	def get_filter_condition(self):
		self.check_mandatory()

		cond = ''
		for f in ['company', 'branch', 'department', 'division', 'designation', 'employee']:
			if self.get(f):
				cond += " and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"

		return cond


        def check_mandatory(self):
		for f in ['company', 'month', 'fiscal_year']:
			if not self.get(f):
				frappe.throw(_("Please set {0}").format(f))

	def get_joining_releiving_condition(self):
		m = get_month_details(self.fiscal_year, self.month)
		cond = """
			and ifnull(t1.date_of_joining, '0000-00-00') <= '%(month_end_date)s'
			and ifnull(t1.relieving_date, '2199-12-31') >= '%(month_start_date)s'
		""" % m
		return cond
	
	def create_increment(self):
		"""
			Creates salary increment for selected employees if already not created
		"""

		emp_list = self.get_emp_list()
		si_list = []
		for emp in emp_list:
                        #frappe.msgprint(_("Employee: {0}, Grade: {1}").format(emp.name, emp.employee_subgroup))
			if not frappe.db.sql("""select name from `tabSalary Increment`
					where docstatus!= 2 and employee = %s and month = %s and fiscal_year = %s and company = %s
					""", (emp.name, self.month, self.fiscal_year, self.company)):
                                payscale = get_employee_payscale(emp.name, emp.employee_subgroup, self.fiscal_year, self.month)
				
				if payscale:
                                        si = frappe.get_doc({
                                                "doctype": "Salary Increment",
                                                "fiscal_year": self.fiscal_year,
                                                "employee": emp.name,
                                                "month": self.month,
                                                "company": emp.company,
                                                "branch": emp.branch,
                                                "department": emp.department,
                                                "division": emp.division,
                                                "section": emp.section,
                                                "employee_subgroup": emp.employee_subgroup,
                                                "payscale_minimum": payscale.minimum,
                                                "payscale_increment": payscale.increment,
                                                "payscale_maximum": payscale.maximum,
                                                "old_basic": payscale.old_basic,
                                                "new_basic": payscale.new_basic,
                                                "increment": payscale.increment,
                                                "employee_name": emp.employee_name,
						"salary_structure": payscale.salary_structure
                                        })
                                        si.insert()
                                        si_list.append(si.name)

		return self.create_log(si_list)

        def remove_increment(self):
                cond = ''
		for f in ['company', 'branch', 'department', 'division', 'designation', 'employee']:
			if self.get(f):
				cond += " and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"

		si_list = frappe.db.sql_list("""
                                select t1.name from `tabSalary Increment` as t1
                                where t1.fiscal_year = '%s'
                                and t1.month = '%s'
                                and t1.docstatus = 0
                                %s
                                """ % (self.fiscal_year, self.month, cond))
                si_log = []
                if si_list:
                        for row in si_list:
                                frappe.delete_doc("Salary Increment", frappe.db.sql_list("""
                                        select t1.name from `tabSalary Increment` as t1
                                        where t1.name = '%s'
                                        """ % row), for_reload=True)
                                si_log.append(row)

                return self.remove_log(si_log)

        def submit_increment(self):
		"""
			Submit all salary increments based on selected criteria
		"""
		cond = ''
		for f in ['company', 'branch', 'department', 'division', 'designation', 'employee']:
			if self.get(f):
				cond += " and t1." + f + " = '" + self.get(f).replace("'", "\'") + "'"

		si_list = frappe.db.sql_list("""
                                select t1.name from `tabSalary Increment` as t1
                                where t1.fiscal_year = '%s'
                                and t1.month = '%s'
                                and t1.docstatus = 0
                                %s
                                """ % (self.fiscal_year, self.month, cond))
                si_log = []
                not_submitted_si = []
                
		for row in si_list:
			si_obj = frappe.get_doc("Salary Increment",row)
			try:
                                si_log.append(row)
				si_obj.submit()
			except Exception,e:
				not_submitted_si.append(row)
				frappe.msgprint(e)
				continue

		return self.submit_log(si_log, not_submitted_si)

	def create_log(self, si_list):
		log = "<p>" + _("No employee for the above selected criteria OR salary increment already created") + "</p>"
		if si_list:
			log = "<b>" + _("Salary Increment Created") + "</b>\
			<br><br>%s" % '<br>'.join(self.format_as_links(si_list))
		return log

	def remove_log(self, si_list):
		log = "<p>" + _("No Records found for the above selected criteria OR salary increment already removed") + "</p>"
		if si_list:
			log = "<b>" + _("Salary Increment Removed") + "</b>\
			<br><br>%s" % '<br>'.join(si_list)
		return log        

        def submit_log(self, si_list, not_submitted_si):
		log = "<p>" + _("No Records found for the above selected criteria OR salary increment already submitted") + "</p>"
		if si_list:
                        log = "<b>" + _("Salary Increment Submitted")
			log += "</b><br><br>%s" % '<br>'.join(self.format_as_links(si_list))
		if not_submitted_si:
                        log += "<br>%s" % '<br>'.join(self.format_as_links(not_submitted_si))
                        
		return log
	
	def format_as_links(self, si_list):
		return ['<a href="#Form/Salary Increment/{0}">{0}</a>'.format(s) for s in si_list]

