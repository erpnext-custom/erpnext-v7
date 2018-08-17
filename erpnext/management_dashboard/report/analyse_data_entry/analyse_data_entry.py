# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.data import get_first_day, get_last_day

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	branch_cond = get_conditions(filters)
	trans = ["tabBreak Down Report","tabJob Card", "tabEquipment Hiring Form", "tabPurchase Order", "tabJournal Entry",\
		"tabPayment Entry", "tabDirect Payment"]

	if filters.get("transaction"):
		if filters.get("transaction") not in ["Material Issue", "Material Transfer", "Material Receipt"]:
			trans = ["tab"+filters.get("transaction")]
		else:
			trans = ''

	date_cond = ''
	for i in trans:
		if i in ["tabBreak Down Report"]:
			date_cond = get_dates(filters, "date")	
		elif i in ["tabJob Card", "tabJournal Entry", "tabPayment Entry", "tabDirect Payment", "Stock Entry"]:
			date_cond = get_dates(filters, "posting_date")
		elif i in ["tabEquipment Hiring Form"]:
			date_cond = get_dates(filters, "request_date")
		else:
			date_cond = get_dates(filters, "transaction_date")
		trans_name = str(i).lstrip("tab").encode('utf-8')
		branch_name = ("'"+filters.get("branch")+"'") if filters.get("branch") else "branch"

		query = """
                        select '{0}' doctype, branch,
                                sum(case when docstatus = 0 then 1 else 0 end) draft,
                                sum(case when docstatus = 1 then 1 else 0 end) submitted,
                                sum(case when docstatus = 2 then 1 else 0 end) cancelled,
                                sum(case when docstatus in (0,1) then 1 else 0 end) total
                        from `{1}`
                        where {2} 
                        and branch = {3}
                        group by doctype, branch
                """.format(trans_name, i, date_cond, branch_name)

		datt = frappe.db.sql(query)
		data.extend(datt)
	entry_purpose = ''
        if not filters.get("transaction"):
		entry_purpose  = ["Material Issue", "Material Transfer", "Material Receipt"]
	if filters.get("transaction"):
		if filters.get("transaction") in ["Material Issue", "Material Transfer", "Material Receipt"]:
                	entry_purpose = [filters.get("transaction")]
		else:
			pass

	for da in entry_purpose:
		branch_name = ("'"+filters.get("branch")+"'") if filters.get("branch") else "branch"
		date_cond = get_dates(filters, "posting_date")
		query1 = """select '{0}' doctype, branch,
					sum(case when docstatus = 0 then 1 else 0 end) draft,
					sum(case when docstatus = 1 then 1 else 0 end) submitted,
					sum(case when docstatus = 2 then 1 else 0 end) cancelled,
					sum(case when docstatus in (0,1) then 1 else 0 end) total
				from `tabStock Entry`
				where purpose = '{0}' and {1}
				and branch = {2}
				group by doctype, branch
			""".format(da,date_cond, branch_name)
                datt = frappe.db.sql(query1)
                data.extend(datt)		
	return data

def get_conditions(filters):
	if filters.get("branch"):
		branch_cond = "'{0}'".format(filters.get("branch"))
	else: 
		branch_cond = " tab.branch"

	return branch_cond


def get_dates(filters, date):
	date_cond = "{0} between '{1}' and '{2}'".format(date, filters.get("from_date"), filters.get("to_date"))
	return date_cond

def get_columns(filters):
	cols = [
                ("Transaction") + ":Data:220",
		("Branch") + ":Data:220",
		("Draf(A)") + ":Int:110",
		("Submitted(B)") + ":Int:110",
		("Cancelled") + ":Int:110",
		("Total(A+B)") + ":Int:110",
	]
	return cols



