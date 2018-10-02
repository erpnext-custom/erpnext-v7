# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname, nowdate, money_in_words, get_first_day
from frappe.model.naming import make_autoname
from frappe import _
from frappe import msgprint
import datetime
#from erpnext.hr.hr_custom_functions import  update_salary_structure

class SalaryIncrement(Document):
        def autoname(self):
		self.name = make_autoname(str(self.employee) + '/.INC/.' + str(self.fiscal_year)+str(self.month)+ '/.#####')
		
        def validate(self):
                self.validate_dates()
		self.validate_increment()

	def on_submit(self):
                self.update_increment(self.new_basic)

        def on_cancel(self):
                self.update_increment(self.old_basic)
                
        def update_increment(self, amount=0):
                if self.salary_structure and amount:
                        sst = frappe.get_doc("Salary Structure", self.salary_structure)
                        sst.update_salary_structure(amount)
                        sst.save(ignore_permissions = True)
        
        def validate_dates(self):
		cur_year = getdate(nowdate()).year
		cur_month= getdate(nowdate()).month

		if int(self.fiscal_year) > int(cur_year):
			frappe.throw(_("Salary Increment Cannot be run for future years."))

		if int(self.fiscal_year) < int(cur_year):
			frappe.throw(_("Salary Increment Cannot be run for past years."))

                '''
		if int(self.month) != int(cur_month):
			frappe.throw(_("Salary Increment Can only be run for the current month."))
                '''
                
	def validate_increment(self):
		inc_list = frappe.db.sql("""
		select name
		from `tabSalary Increment`
		where employee = '%s'
		and fiscal_year = '%s'
		and month = '%s'
		and salary_structure = '%s'
		and docstatus = 1
		""" % (self.employee, self.fiscal_year, self.month, self.salary_structure))

		if inc_list:
			frappe.msgprint("Salary Increment is already processed for Employee '{0} {1}'\
					for the Month: {2} and Year: {3}".format(self.employee, self.employee_name, \
					self.month, self.fiscal_year))

@frappe.whitelist()
def get_employee_payscale(employee, gradecd, fiscal_year, month):
        payscale = frappe.db.get_value("Employee Grade", filters=gradecd, \
                                       fieldname = ["minimum","maximum","increment", "increment_percent"], as_dict = True)
        sal_struc_name = get_salary_structure(employee)
        
        if payscale:
                sal_struc= frappe.get_doc("Salary Structure",sal_struc_name)
		if not sal_struc:
			frappe.throw("No Active Salary Structure Found")
                old_basic = 0.00
                new_basic = 0.00
                for d in sal_struc.earnings:
                        if d.salary_component == 'Basic Pay':
                                old_basic = flt(d.amount)

                if old_basic:
			if payscale.increment_percent > 0:
				payscale["increment"] = flt(flt(old_basic) * flt(payscale.increment_percent) * 0.01)
                        new_basic = flt(old_basic if old_basic else 0) + flt(payscale.increment if payscale.increment else 0.00)

                payscale["old_basic"] = flt(old_basic if old_basic else 0.00)
                payscale["new_basic"] = new_basic
		payscale["salary_structure"] = sal_struc.name
        else:
                frappe.throw(_('Pay Scale not defined for grade: <a style="color: green" href="#Form/Employee Grade/{0}">{0}</a>').format(gradecd))
        
        return payscale

def get_salary_structure(employee):
        salary_struc_list = frappe.db.sql("""
                        select name from `tabSalary Structure`
                        where employee = %s
                        and is_active = 'Yes'
                        order by ifnull(from_date,'0000-00-00') desc limit 1
                """,(employee))

        if salary_struc_list:
                return salary_struc_list[0][0]
        else:
                frappe.throw(_('No Active Salary Structure found for the employee <a style="color: green" href="#Form/Employee/{0}">{0}</a>.').format(employee))
                        
        return salary_struc_list[0][0]
