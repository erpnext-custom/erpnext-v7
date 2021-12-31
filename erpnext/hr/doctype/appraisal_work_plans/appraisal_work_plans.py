# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import flt, getdate, cint

from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document
from erpnext.hr.utils import set_employee_name

class AppraisalWorkPlan(Document):
    def validate(self):

        #if not self.status:
        #	self.status = "Draft"

        set_employee_name(self)
        self.validate_dates()
        self.check_total_points()
        self.validate_existing_appraisal_work_plan()
        #self.calculate_total()
    def get_employee_name(self):
        self.employee_name = frappe.db.get_value("Employee", self.employee, "employee_name")
        return self.employee_name


# check end date should always gratter then start date
    def validate_dates(self):
        if getdate(self.start_date) > getdate(self.end_date):
            frappe.throw(_("End Date can not be less than Start Date"))
    
#searching deplication of work plan or already exit on given date range
    def validate_existing_appraisal_work_plan(self):
        chk = frappe.db.sql("""select name from `tabAppraisal Work Plan` 
            where employee=%(employee)s and docstatus <2 and status in ("Draft")
            
            and end_date >= %(start_date)s and start_date <= %(end_date)s
            and name != %(name)s""", {
                "employee": self.employee,
                "start_date": self.start_date,
                "end_date": self.end_date,
                "name": self.name
            })

        if chk:
            frappe.throw(_("Appraisal Work Plan {0} created for Employee {1} in the given date range").format(chk[0][0], self.employee_name))

    #check total weightage, its should not more than 100
    def check_total_points(self):	
        total_points = 0
        frappe.throw("ahshadgh")
        for d in self.get("goals"):
            total_points += int(d.per_weightage or 0)

        if cint(total_points) != 100:
            frappe.throw(_("Sum of points for all goals should be 100. It is {0}").format(total_points))
        
        

        