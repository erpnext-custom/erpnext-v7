# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	cond = ""
	payment_cond = ""
	if filters.get("from_date") and filters.get("to_date"):
		cond += " and rp.posting_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
	if filters.get("workflow_state"):
		cond += " and rp.workflow_state = '{0}'".format(filters.get("workflow_state"))
	if filters.get("cost_center"):
		if not filters.get("branch"):
			all_ccs = get_child_cost_centers(filters.get("cost_center"))
			cond += " and rp.branch in (select b.name from `tabBranch` b where b.cost_center in {0})".format(tuple(all_ccs))
		else:
			branch_name = frappe.db.get_value("Branch",{"cost_center": filters.get("branch")}, "name") 
			cond += " and rp.branch = '{0}'".format(branch_name)
	if filters.get("payment_state"):
		payment_cond += " and data.status = '{0}'".format(filters.get("payment_state"))
	
	if filters.get("range"):
		cond += " and rp.range_name = '{0}'".format(filters.get("range"))

	if filters.get("ref_id"):
		cond += " and rp.name = '{0}'".format(filters.get("ref_id"))
	
	if filters.get("payment_id"):
		cond += " and rp.journal_entry = '{0}'".format(filters.get("payment_id"))
	
	if filters.get("item_sub_group"):
		if filters.get("detail"):
			if filters.get("item_sub_group") in ('Firewood, Bhutan Furniture','BBPL firewood','Firewood(BBPL)','Firewood (Bhutan Ply)','Firewood','Post','Bakals','Woodchips','Briquette','Off-cuts/Sawn timber waste','Off-Cuts','Saw Dust'):
				cond += " and rpa.particular in (select item_name from `tabItem` where item_sub_group = '{0}' )".format(filters.get("item_sub_group"))
			else:
				cond += " and rpa.particular = '{0}'".format(filters.get("item_sub_group"))
		else:
			frappe.throw("This filter in only applicable in detailed mode")
	
	if filters.get("timber_class"):
		if filters.get("detail"):
			cond += " and rpa.timber_class = '{0}'".format(filters.get("timber_class"))
		else:
			frappe.throw("This filter in only applicable in detailed mode")
	
	if filters.get("quantity"):
		if filters.get("detail"):
			cond += " and rpa.quantity = '{0}'".format(filters.get("quantity"))
		else:
			frappe.throw("This filter in only applicable in detailed mode")
	
	if filters.get("rate"):
		if filters.get("detail"):
			cond += " and rpa.rate = '{0}'".format(filters.get("rate"))
		else:
			frappe.throw("This filter in only applicable in detailed mode")

	# query = frappe.db.sql("""
	# 	select *from ( select ml.branch, ml.production_type, ml.posting_date, ml.name
    #             from
    #             `tabMarking List` ml  
    #             where ml.docstatus =1 {0}) as m
    #             left join
    #             (select rp.name, rp.journal_entry, rp.total_royalty, rp.marking_list
    #             from
	# 	`tabRoyalty Payment` rp 
    #             where rp.docstatus =1) as r
    #             on m.name = r.marking_list""".format(cond))
	
	#Above query commented and below query added for new Royalty Payment Report //Kinley Dorji 2021-02-17
	if not filters.get("detail"):
		query = frappe.db.sql("""
			select * from (
			select rp.posting_date as posting_date, rp.name as name, rp.workflow_state as workflow_state, rp.branch as branch, rp.range_name as range_name, rp.production_type as production_type, ifnull(rp.journal_entry,'None') as journal_entry, rp.business_activity as business_activity, rp.total_royalty, rp.discount_amount, rp.net_royalty, rp.total_qty, rp.less_qty, rp.net_qty,
			CASE WHEN (select je.docstatus from `tabJournal Entry` je where je.name = rp.journal_entry and rp.docstatus = 1) = 1 THEN 'Paid'
			WHEN (select je.docstatus from `tabJournal Entry` je where je.name = rp.journal_entry and rp.docstatus = 1) = 0 THEN 'Due'
			ELSE 'None' END AS status	
			from `tabRoyalty Payment` rp where rp.docstatus != 2 {0}
			) as data where 1 = 1 {1}
		""".format(cond, payment_cond))
	else:
		# if filters.get()
		query = frappe.db.sql("""
			select * from (
			select rp.posting_date as posting_date, rpa.particular , rp.name as name, rp.workflow_state as workflow_state, rp.branch as branch, rp.range_name as range_name, rp.production_type as production_type, ifnull(rp.journal_entry,'None') as journal_entry, rp.business_activity as business_activity, rpa.quantity, rpa.rate, rpa.amount, rpa.timber_class, rpa.reading,
			CASE WHEN (select je.docstatus from `tabJournal Entry` je where je.name = rp.journal_entry and rp.docstatus = 1) = 1 THEN 'Paid'
			WHEN (select je.docstatus from `tabJournal Entry` je where je.name = rp.journal_entry and rp.docstatus = 1) = 0 THEN 'Due'
			ELSE 'None' END AS status	
			from `tabRoyalty Payment` rp, `tabRoyalty Payment Adhoc` rpa where rp.name = rpa.parent and rp.docstatus != 2 {0}
			) as data where 1 = 1 {1}
		""".format(cond, payment_cond))
	return query

def get_columns(filters):
	if not filters.get("detail"):
		columns = [
			("Date") + "::80",
			("Royalty Payment ID") + ":Link/Royalty Payment:150",
			("Workflow State") + "::100",	
			("Branch") + ":Link/Branch:150",
			("Range Name") + "::150",
			("Production Type") + "::140",
			# ("Marking List ID") + ":Link/Marking List:120",
			("Journal Entry") + ":Link/Journal Entry:120",
			("Business Activity") + "::140",
			("Total Royalty") + ":Currency:140",
			("Discount") + ":Currency:140",
			("Net Royalty") + ":Currency:140",
			("Total Quantity") + ":Float:140",
			("Subracted Quantity") + ":Float:140",
			("Net Quantity") + ":Float:140",
			("Status") + "::140",
		]
	else:
		columns = [
			("Date") + "::80",
			("Particular") + "::150",
			("Royalty Payment ID") + ":Link/Royalty Payment:150",
			("Workflow State") + "::100",	
			("Branch") + ":Link/Branch:150",
			("Range Name") + "::150",
			("Production Type") + "::140",
			# ("Marking List ID") + ":Link/Marking List:120",
			("Journal Entry") + ":Link/Journal Entry:120",
			("Business Activity") + "::140",
			("Quantity") + ":Float:140",
			("Royalty Rate") + "::100",
			("Amount") + ":Float:140",
			("Timber Class") + "::100",
			("Reading") + "::100",
			("Status") + "::140",
		]
	return columns
