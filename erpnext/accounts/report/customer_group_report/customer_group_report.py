# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
	columns =get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return  [
		("Branch") + ":Data:150",
		("Domestic")+ ":Currency:150",
		("Internal") + ":Currency:150",
		("Government Institutions") +":Currency:150",
		("Government Organizations/Institutions") +":Currency:150",
		("All Customer Groups") + ":Currency:150",
		("Exporters") + ":Currency:150",
		("AWBI")+ ":Currency:150",
		("Corporate Agency") + ":Currency:150",
		("International Agency") +":Currency:150",
		("Dzongs") +":Currency:150",
		("Dzongs & Lhakhang Constructions")+ ":Currency:150",
		("Lhakhangs & Goendey") + ":Currency:150",
		("Arm Force") + ":Currency:150",
		("Furniture Units")+ ":Currency:150",
		("Rural") +":Currency:150",
		("Royal & VVIP") + ":Currency:150",
		("Crushing Plants") +":Currency:150",
		("Special project: VVIP")+ ":Currency:150",
		("Contractor for Hydropower project")+ ":Currency:150",
		("Contractors for Govt. Projects")+ ":Currency:150",
	]


def get_data(filters):
	query ="""select branch as Branch, 
		sum(case when customer_group = 'Domestic' then grand_total else 0 end) as 'Domestic', 
		sum(case when customer_group ='Internal-NRDCL' then grand_total else 0 end) as 'Internal', 
		sum(case when customer_group ='Government Institutions' then grand_total else 0 end) as 'Government Institutions', 
		sum(case when customer_group ='Government Organizations/Institutions' then grand_total else 0 end) as 'Government Organizations/Institutions', 
		sum(case when customer_group ='All Customer Groups' then grand_total else 0 end) as 'All Customer Groups', 
		sum(case when customer_group ='Exporters' then grand_total else 0 end) as 'Exporters', 
		sum(case when customer_group ='AWBI' then grand_total else 0 end) as 'AWBI', 
		sum(case when customer_group ='Corporate Agency' then grand_total else 0 end) as 'Corporate Agency', 
		sum(case when customer_group ='International Agency' then grand_total else 0 end) as 'International Agency',
		sum(case when customer_group ='Dzongs' then grand_total else 0 end) as 'Dzongs', 
		sum(case when customer_group ='Dzongs & Lhakhang Constructions' then grand_total else 0 end) as 'Dzongs & Lhakhang Constructions', 
		sum(case when customer_group ='Lhakhangs & Goendey' then grand_total else 0 end) as 'Lhakhangs & Goendey',  
		sum(case when customer_group ='Armed Force' then grand_total else 0 end) as 'Arm Force', 
		sum(case when customer_group ='Furniture Units' then grand_total else 0 end) as 'Furniture Units', 
		sum(case when customer_group ='Rural' then grand_total else 0 end) as 'Rural', 
		sum(case when customer_group ="People's Project" then grand_total else 0 end) as 'Royal & VVIP', 
		sum(case when customer_group ='Crushing Plants' then grand_total else 0 end) as 'Crushing Plants', 
		sum(case when customer_group ='Special project: VVIP' then grand_total else 0 end) as 'Special project: VVIP', 
		sum(case when customer_group ='Contractor for Hydropower projects' then grand_total else 0 end) as 'Contractor for Hydropower projects', 
		sum(case when customer_group ='Contractors for Govt. Projects' then grand_total else 0 end) as 'Contractors for Govt. Projects'
	from `tabSales Invoice` where docstatus = 1 """
	
	if not filters.cost_center:
		return ""

	if not filters.branch:	
		all_ccs = get_child_cost_centers(filters.cost_center)
		query += " and branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))
	else:
		branch = str(filters.get("branch"))
		branch = branch.replace(' - NRDCL','')
		query += " and branch = \'"+branch+"\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	query += " group by branch"

	return frappe.db.sql(query)