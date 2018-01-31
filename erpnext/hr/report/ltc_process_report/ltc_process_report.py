# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)
        return columns, data

def get_data(filters):
        query = """
                select ltcd.employee, ltcd.employee_name,  
                ltcd.branch, ltcd.bank_name, ltcd.bank_ac_no, ltcd.amount 
                from `tabLeave Travel Concession` ltc, `tabLTC Details` ltcd 
                where ltcd.parent = ltc.name and ltc.docstatus = 1"""

        if filters.get("fy"):
                query += " and ltc.fiscal_year = \'"+ str(filters.fy) + "\'"
        return frappe.db.sql(query)

def get_columns():
        return [
                ("Employee ID ") + ":Link/Employee:150",
                ("Name") + ":Data:110",
                ("Branch") + ":Data:280",
                ("Bank Name") + ":Data:100",
                ("A/C No")+ ":Data:110",
                ("Amount") + ":Currency:130"
        ]

