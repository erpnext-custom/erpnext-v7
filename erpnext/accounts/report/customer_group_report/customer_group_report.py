# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns =get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return  [
		("Branch") + ":Data:100",
		("Domestic")+ ":Data:100",
		("Internal") + ":Data:100",
		("Government Organization") +":Data:100",
		("All Customer Group") + ":Data:100",
                ("AWBI")+ ":Data:100",
                ("Corporate Agency") + ":Data:100",
                ("International") +":Data:100",
		]


def get_data(filters):
	query ="""select branch, case when customer_group = 'Domestic' then sum(grand_total) end as 'Domestic', case when customer_group ='Internal' then sum(grand_total) end as 'Internal', case when customer_group ='Government Organization' then sum(grand_total) end as 'Government Organization', case when customer_group ='All Customer Groups' then sum(grand_total) end as 'All Customer Groups', case when customer_group ='AWBI' then sum(grand_total) end as 'AWBI', case when customer_group ='Corporate Agency' then sum(grand_total) end as 'Corporate Agency', case when customer_group ='International' then sum(grand_total) end as 'International' from `tabSales Invoice` where docstatus = 1 """
	
	if filters.get("branch"):
		query += " and branch = \'"+ str(filters.branch) + "\'"

        if filters.get("from_date") and filters.get("to_date"):
		query += " and posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	query += " group by branch"
	return frappe.db.sql(query)		
