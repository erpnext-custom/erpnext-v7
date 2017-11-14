# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SSK		 14/11/2017                           Original
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
        data    = get_data(filters)
        columns = get_columns()
	return columns, data

def get_data(filters):
        data = []
        result = frappe.db.sql("""
                        select distinct
                                p.name          as project_id,
                                p.project_name  as project_name,
                                p.branch        as branch,
                                p.cost_center   as cost_center,
                                wh.parenttype   as employee_type,
                                wh.parent       as employee,
                                e.employee_name as employee_name,
                                e.designation   as designation,
                                e.status        as status,
                                'Project'       as doctype,
                                p.name          as docname
                        from `tabProject` as p,
                             `tabEmployee Internal Work History` as wh
                        left join `tabEmployee` as e
                        on e.employee = wh.parent
                        where p.name    = "{0}"
                        and   wh.branch = p.branch
                        order by project_id, employee_type, employee 
                        """.format(filters.get("project")), as_dict=1)

        for i in result:
                if i.employee_type.lower() in ('gep employee','muster roll employee'):
                        other = frappe.db.sql("""
                                select
                                        person_name,
                                        status
                                from `tab{0}`
                                where name = '{1}'
                        """.format(i.employee_type, i.employee), as_dict=1)[0]

                        if other:
                                i["employee_name"] = other.person_name
                                i["status"] = other.status
                        
                data.append(i)
        return result
        
def get_columns():
        return [
                {
                        "fieldname": "project_id",
                        "label": _("Project"),
                        "fieldtype": "Link",
                        "options": "Project",
                        "width": 300
                },
                {
                        "fieldname": "employee",
                        "label": _("Employee ID"),
                        "width": 100
                },
                {
                        "fieldname": "employee_name",
                        "label": _("Employee Name"),
                        "width": 150
                },
                {
                        "fieldname": "designation",
                        "label": _("Designation"),
                        "width": 150
                },
                {
                        "fieldname": "employee_type",
                        "label": _("Type"),
                        "width": 100
                },
                {
                        "fieldname": "status",
                        "label": _("Status"),
                        "width": 80
                },
                {
                        "fieldname": "branch",
                        "label": _("Branch"),
                        "fieldtype": "Link",
                        "options": "Branch",
                        "width": 100
                },
                {
                        "fieldname": "cost_center",
                        "label": _("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "width": 100
                },
        ]

