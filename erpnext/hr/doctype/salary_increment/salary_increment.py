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

class SalaryIncrement(Document):
        def autoname(self):
		self.name = make_autoname(self.employee + '/.INC/.' + self.fiscal_year+self.month+ '/.#####')
		
        def validate(self):
                self.validate_dates()
		self.validate_increment()

	def on_submit(self):
		if self.docstatus == 1:
			self.update_salary_structure(self.employee, self.increment)

        def validate_dates(self):
		cur_year = getdate(nowdate()).year
		cur_month= getdate(nowdate()).month

		if int(self.fiscal_year) > int(cur_year):
			frappe.throw(_("Salary Increment Cannot be run for future years."))

		if int(self.fiscal_year) < int(cur_year):
			frappe.throw(_("Salary Increment Cannot be run for past years."))

		if int(self.month) != int(cur_month):
			frappe.throw(_("Salary Increment Can only be run for the current month."))

	def validate_increment(self):
		inc_list = frappe.db.sql("""
		select name
		from `tabSalary Increment`
		where employee = '%s'
		and fiscal_year = '%s'
		and month = '%s'
		and docstatus = 1
		""" % (self.employee, self.fiscal_year, self.month))

		if inc_list:
			frappe.msgprint("Salary Increment is already processed for Employee '{0} {1}'\
					for the Month: {2} and Year: {3}".format(self.employee, self.employee_name, \
					self.month, self.fiscal_year))

	def update_salary_structure(self, employee, increment):

		sal_struc_name = frappe.db.sql("""
		select name
		from `tabSalary Structure` st
		where st.employee = '%s'
		and is_active = 'Yes'
		and now() between ifnull(from_date,'0000-00-00') and ifnull(to_date,'2050-12-31')
		order by ifnull(from_date,'0000-00-00') desc 
		limit 1
		""" % (self.employee))
		
		sst = ""
		if sal_struc_name and increment > 0:
			sst = frappe.get_doc("Salary Structure", sal_struc_name[0][0])
			for row in sst.earnings:
				if row.salary_component == "Basic Pay":
					row.db_set('amount',flt(row.amount)+flt(increment),update_modified=True)
					#row.update('amount',flt(row.amount)+flt(increment))

		if sst:
			sst.update()
			sst.save()

@frappe.whitelist()
def get_employee_payscale(employee, gradecd, fiscal_year, month):
        payscale = frappe.db.get_value("Employee Sub-Group", filters=gradecd, \
                                       fieldname = ["minimum","maximum","increment"], as_dict = True)
        sal_struc_name = get_salary_structure(employee)
        
        if payscale:
                sal_struc= frappe.get_doc("Salary Structure",sal_struc_name)
                old_basic = 0.00
                new_basic = 0.00
                for d in sal_struc.earnings:
                        if d.salary_component == 'Basic Pay':
                                old_basic = flt(d.amount)

                if old_basic:
                        new_basic = flt(old_basic if old_basic else 0) + flt(payscale.increment if payscale.increment else 0.00)

                payscale["old_basic"] = flt(old_basic if old_basic else 0.00)
                payscale["new_basic"] = new_basic
        else:
                frappe.throw(_('Pay Scale not defined for grade: <a style="color: green" href="#Form/Employee Sub-Group/{0}">{0}</a>').format(gradecd))
        
        return payscale

def get_salary_structure(employee):
        salary_struc_list = frappe.db.sql("""
                        select name from `tabSalary Structure`
                        where employee = %s
                        and is_active = 'Yes'
                        and now() between ifnull(from_date,'0000-00-00') and ifnull(to_date,'2050-12-31')
                        order by ifnull(from_date,'0000-00-00') desc limit 1
                """,(employee))

        if salary_struc_list:
                return salary_struc_list[0][0]
        else:
                frappe.throw(_('No Active Salary Structure found for the employee <a style="color: green" href="#Form/Employee/{0}">{0}</a>.').format(employee))
                        
        return salary_struc_list[0][0]
