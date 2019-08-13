# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr
from frappe import msgprint, _

def execute(filters=None):
        if not filters: filters = {}
        data    = []
        columns = []

        data = get_data(filters)
        if not data:
                return columns, data

        columns = get_columns(data)

        return columns, data

def get_columns(data):
        columns = [
                _("GIS Number") + "::100",
                _("Employee") + ":Link/Employee:100",
                _("CID") + "::110",
                _("Employee Name") + "::140",
                _("Date Of Joining") + "::100",
                _("Group") + "::100",
                _("Grade") + "::60",
                _("Policy Number") + "::100",
                _("GIS Contribution") + ":Currency:120",
                _("Status") + "::80"
        ]

        return columns

def get_data(filters):
        conditions, filters = get_conditions(filters)
        data = frappe.db.sql("""select 
                               t1.gis_number, t1.employee as n, t3.passport_number, t3.employee_name,  
                                 t3.date_of_joining, t3.employee_group, t1.employee_subgroup,  t1.gis_policy_number,
                               
                                sum(case when t2.salary_component = 'Group Insurance Scheme' then ifnull(t2.amount,0) else 0 end) as gisamount,
                                t3.status
                                from `tabSalary Slip` t1, `tabSalary Detail` t2, `tabEmployee` t3
                                where t1.docstatus = 1 %s
                                and t3.employee = t1.employee
                                and t2.parent = t1.name
                                and t2.salary_component in ('Basic Pay','Group Insurance Scheme')
                                group by t1.employee, t3.employee_name, t1.designation, t3.passport_number,  t3.gis_number, 
                                t1.company, t1.branch, t1.department, t1.division, t1.section, t1.fiscal_year, t1.month
                """ % conditions, filters)

        '''
        if not data:
                msgprint(_("No Data Found for month: ") + cstr(filters.get("month")) +
                        _(" and year: ") + cstr(filters.get("fiscal_year")), raise_exception=1)
        '''

        return data

def get_conditions(filters):
        conditions = ""
        if filters.get("month"):
                month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                        "Dec"].index(filters["month"]) + 1
                filters["month"] = month
                conditions += " and t1.month = %(month)s"

        if filters.get("fiscal_year"): conditions += " and t1.fiscal_year = %(fiscal_year)s"
        if filters.get("company"): conditions += " and t1.company = %(company)s"
        if filters.get("employee"): conditions += " and t1.employee = %(employee)s"

        return conditions, filters

