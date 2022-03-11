# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# --------------------------------------------------------------------
# CREATED BY BIREN AND MOVED TO PRODUCTION ON DECEMBER 14. 
# --------------------------------------------------------------------

from __future__ import unicode_literals
import frappe
from frappe.utils import cint

def execute(filters=None):
    columns = data = []
    if  filters.get('accumulate_data'):
        columns, data = get_all_column(filters), get_all_data(filters)
    else:
        columns, data = get_columns(filters), get_data(filters)
    return columns, data

def get_all_column(filters):
    return [
         {
            "fieldname":"type",
            "label":"Type",
            "fieldtype":"Data",
            "width":200
        },
        {
            "fieldname":"number",
            "label":"Count",
            "fieldtype":"Int",
            "width":200
        },
        ]

def get_all_data(filters):
    data = []
    for d in frappe.db.sql('''
                           SELECT SUM(CASE WHEN gender = 'Male' AND status = 'Active' THEN 1 ELSE 0 END) as male,
                            SUM(CASE WHEN gender = 'Female' AND status = 'Active' THEN 1 ELSE 0 END) as female,
                            SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active,
                            SUM(CASE WHEN status = 'Left' THEN 1 ELSE 0 END) as `left` FROM `tabEmployee`''',as_dict = 1):
        data.append({ 'type':'<b>Gender</b>' })
        data.append({ 'type':'Male','number':d.male})
        data.append({ 'type':'Female','number':d.female})
        data.append({ 'type':'<b>Status</b>' })
        data.append({ 'type':'Active','number':d.active})
        data.append({ 'type':'Left','number':d.left})
        
    data.append({ 'type':'<b>Employement Type</b>'})
    data += frappe.db.sql('''SELECT COUNT(*) as number, employee_group as type FROM `tabEmployee` WHERE status='Active' GROUP BY employment_type''',as_dict = 1)
    data.append({ 'type':'<b>EMPLOYEE GROUP</b>'})
    data += frappe.db.sql('''SELECT COUNT(*) as number, employee_group as type FROM `tabEmployee` WHERE status='Active' GROUP BY employee_group''',as_dict = 1)
    data.append({ 'type':'<b>EMPLOYEE GRADE</b>'})
    data += frappe.db.sql('''SELECT COUNT(*) as number,employee_subgroup as type FROM `tabEmployee` WHERE status='Active' GROUP BY employee_subgroup''',as_dict = 1)
    return data

def get_data(filters):
    conditions = get_conditions(filters)
    query = ''
    if filters.get('qualification'):
        query = """
            SELECT 
                e.name, e.employee_name, e.gender,
                e.status, e.date_of_joining, e.employment_type,
                e.employee_group, e.employee_subgroup, e.branch,
                e.department, e.division, e.bank_name,
                e.bank_ac_no,e.increment_and_promotion_cycle,
                e.cost_center, ee.qualification,ee.trade,ee.level
            FROM 
                `tabEmployee` e, `tabEmployee Education` ee where e.name = ee.parent 
            {}
        """.format(conditions)
    else:
        query = """
            SELECT 
                e.name, e.employee_name, e.gender, e.company,
                e.status, e.date_of_joining, e.employment_type,
                e.employee_group, e.employee_subgroup, e.branch,
                e.department, e.division, e.bank_name,
                e.bank_ac_no,e.increment_and_promotion_cycle,
                e.cost_center
            FROM 
                `tabEmployee` e where docstatus in (1,0) 
                {}
        """.format(conditions)
    data = frappe.db.sql(query)
    return data

def get_conditions(filters):
    conditions = ""
    if filters.company:
         conditions += " and e.company='{}'".format(filters.company)

    if filters.get("employment_type"):
        conditions += " e.employment_type = '{}'".format(filters.get("employment_type"))
        
    if filters.get("status"):
        conditions += " and e.status = '{}'".format(filters.get("status"))
    return conditions


def get_columns(filters):

    columns = [
            ("Employee ID") + ":Link/Employee:120",
            ("Employee Name") + ":Data:200",
            ("Gender") + ":Data:50",
            ("Status") + ":Data:50",
            ("Date of Joining") + ":Data:150",
            ("Employment Type") + ":Data:150",
            ("Employee Group") + ":Data:200",
            ("Employee Sub Group") + ":Data:200",
            ("Branch") + ":Data:250",
            ("Department") + ":Data:250",
            ("Division") + ":Data:250",
            ("Bank Name") + ":Data:150",
            ("bank Acc No") + ":Data:120",
            ("Increment Cycle") + ":Data:110",
            ("Cost Center") + ":Data:200",
    ]
    if filters.get('qualification'):
        columns += [("Qualification") + ":Data:120",
                    ("Trade") + ":Data:120",
                    ("Level") + ":Data:120"]
    return columns