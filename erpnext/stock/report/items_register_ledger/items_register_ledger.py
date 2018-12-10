# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def execute(filters = None):
        columns = get_columns(filters)
        data = get_data(filters)
        return columns, data

def get_columns(filters):
        cols =  [
                ("Doc ID") + ":Link/Consumable Register Entry:120", ("Material Code") + ":Link/Item:120", ("Material Name") + ":Data:120",
                ("Posting Date") + ":Date:120", ("Employee ID")+ ":Link/Employee:100", ("Employee Name") + ":Data:120", ("Quantity") + ":Data:70",
                ("Ref Document")+ ":Link/Stock Entry:150"
        ]
        cols1 = [
                ("Material Code") + ":Link/Item:120", ("Material Name") + ":Data:120",
                ("Employee ID")+ ":Link/Employee:100", ("Employee Name") + ":Data:120", ("Quantity") + ":Data:70"
        ]
        if filters.get("option") == 'Summarized':
                column = cols1
        if filters.get("option") == 'Detail':
                column = cols
        return column

def get_data(filters):
        #frappe.msgprint("this is testing")
        query = ''
        dat = " and 1 =1"
	branch = " 1 =1"
	if filters.get("branch"):
		branch = " a.branch =  '{0}'".format(filters.get("branch"))

        if filters.get("from_date") and filters.get("to_date"):
                dat  = " and a.date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

        if filters.get("option") == 'Detail':
                query =  """ select a.name, a.item_code, (select b.item_name from tabItem b where b.item_code = a.item_code) as item_name, 
                        a.date, a.issued_to, (select c.employee_name from tabEmployee c where c.name = a.issued_to) as employee_name, 
                        a.qty, a.ref_doc from `tabConsumable Register Entry` a  where {0} {1}""".format(branch, dat)

        if filters.get("option") == 'Summarized':
                query =  """ select a.item_code, (select b.item_name from tabItem b where b.item_code = a.item_code) as item_name, 
                        a.issued_to, (select c.employee_name from tabEmployee c where c.name = a.issued_to)  as employee_name, sum(a.qty) from `tabConsumable Register Entry` a  
                        where {0} {1} """.format(branch, dat)
                query += " group by a.item_code, employee_name having sum(a.qty) > 0"
        return frappe.db.sql(query)

