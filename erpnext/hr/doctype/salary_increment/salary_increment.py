# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname, nowdate, money_in_words


class SalaryIncrement(Document):
	pass

@frappe.whitelist()
def get_employee_payscale(employee, gradecd):
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
