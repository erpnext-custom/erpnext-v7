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
		("Private") + ":Data:100",		
		("Projects") + ":Data:100",		
		("Government Institutions") +":Data:100",
		("All Customer Group") + ":Data:100",
        ("AWBI")+ ":Data:100",
        ("Corporate Agency") + ":Data:100",
        ("International") +":Data:100",
		("Dzongs") +":Data:100",
        ("Arm Force") + ":Data:100",
        ("Furniture Units")+ ":Data:100",
        ("Royal & VVIP") + ":Data:100",
        ("Rural") +":Data:100",
		("Lhakhangs & Goendey") +":Data:100",
				
		]


def get_data(filters):
	query ="""select branch,
	sum(case when customer_group = 'Domestic' then grand_total end) as 'Domestic', 
	sum(case when customer_group ='Internal' then grand_total end) as 'Internal', 
	sum(case when customer_group ='Private' then grand_total end) as 'Private',
	sum(case when customer_group ='Projects' then grand_total end) as 'Projects', 
	sum(case when customer_group ='Government Institutions' then grand_total end) as 'Government Institutions', 
	sum(case when customer_group ='All Customer Groups' then grand_total end) as 'All Customer Groups', 
	sum(case when customer_group ='AWBI' then grand_total end) as 'AWBI', 
	sum(case when customer_group ='Corporate Agency' then grand_total end) as 'Corporate Agency', 
	sum(case when customer_group ='International Customer' then grand_total end) as 'International',
	sum(case when customer_group ='Dzongs' then grand_total end) as 'Dzongs', 
    sum(case when customer_group ='Arm Force' then grand_total end) as 'Arm Force', 
    sum(case when customer_group ='Furniture Units' then grand_total end) as 'Furniture Units', 
    sum(case when customer_group ='Royal & VVIP' then grand_total end) as 'Royal & VVIP', 
    sum(case when customer_group ='Rural' then grand_total end) as 'Rural', 
    sum(case when customer_group ='Lhakhangs & Goendey' then grand_total end) as 'Lhakhangs'  
	from `tabSales Invoice` where docstatus = 1"""
	
	if filters.get("branch"):
		query += " and branch = \'"+ str(filters.branch) + "\'"

    	if filters.get("from_date") and filters.get("to_date"):
		query += " and posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	
	query += " group by branch"
	return frappe.db.sql(query)		
