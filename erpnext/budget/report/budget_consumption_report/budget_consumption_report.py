# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.accounts.accounts_custom_functions import get_child_cost_centers

def execute(filters=None):
	validate_filters(filters)
	columns = get_columns()
	queries = construct_query(filters)
	data = get_data(queries, filters)

	return columns, data

def get_data(query, filters):
	data = []
	datas = frappe.db.sql(query, as_dict=True)
	ini = su = cm = co = ad = ads = av = adj = 0
	for d in datas:
		if filters.group_by_account:
			d.cost_center = ""
			committed = frappe.db.sql("select SUM(amount) from `tabCommitted Budget` where account = %s and po_date BETWEEN %s and %s", (d.account, filters.from_date, filters.to_date))[0][0]
			consumed = frappe.db.sql("select SUM(amount) from `tabConsumed Budget` where account = %s and po_date BETWEEN %s and %s", (d.account, filters.from_date, filters.to_date))[0][0]
		else:
			committed = frappe.db.sql("select SUM(amount) from `tabCommitted Budget` where cost_center = %s and business_activity = %s and account = %s and po_date BETWEEN %s and %s", (d.cost_center, d.business_activity, d.account, filters.from_date, filters.to_date))[0][0]
			consumed = frappe.db.sql("select SUM(amount) from `tabConsumed Budget` where cost_center = %s and business_activity = %s and account = %s and po_date BETWEEN %s and %s", (d.cost_center, d.business_activity, d.account, filters.from_date, filters.to_date))[0][0]
		if not committed:
			committed = 0
		if not consumed:
			consumed = 0
			
		adjustment = flt(d.added) - flt(d.deducted)
		supplement = flt(d.supplement)
		if committed != 0:
			committed-=consumed
			if committed < 0:
				committed = 0
		
		available = flt(d.initial_budget) + flt(adjustment) + flt(d.supplement) - consumed - committed
		row = {
			"account": d.account, 
			"cost_center": d.cost_center,
			"business_activity": d.business_activity,
			"initial": flt(d.initial_budget),
			"supplementary": supplement,
			"adjustment_add": d.added,
			"adjustment_sent": d.deducted,
			"adjustment": adjustment,
			"committed": committed,
			"consumed": consumed,
			"available": available
		}
		data.append(row)
		ini+=flt(d.initial_budget)
		su+=supplement
		cm+=committed
		co+=consumed
		ad+=flt(d.added)
		ads+=flt(d.deducted)
		adj+=adjustment
		av+=available

	row = {
		"account": "Total",
		"cost_center": "",
		"initial": ini,
		"supplementary": su,
		"adjustment_add": ad,
		"adjustment_sent": ads,
		"adjustment": adj,
		"committed": cm,
		"consumed": co,
		"available": av
	}
	data.append(row)

	return data

def construct_query(filters=None):
	if filters.group_by_account:
		filters.cost_center = None
	#query = "select b.cost_center, ba.account, ba.budget_amount, ba.initial_budget, ba.budget_received as added, ba.budget_sent as deducted, ba.supplementary_budget as supplement, (select SUM(amount) from `tabCommitted Budget` cb where cb.cost_center = b.cost_center and cb.account = ba.account and cb.po_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\') as committed, (select SUM(amount) from `tabConsumed Budget` conb where conb.cost_center = b.cost_center and conb.account = ba.account and conb.po_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\') as consumed from `tabBudget` b, `tabBudget Account` ba where b.docstatus = 1 and b.name = ba.parent and b.fiscal_year = " + str(filters.fiscal_year)
	query = """select b.cost_center, b.business_activity, ba.account, SUM(ba.budget_amount) as budget_amount, 
				SUM(ba.initial_budget) as initial_budget, SUM(ba.budget_received) as added, SUM(ba.budget_sent) as deducted, 
				SUM(ba.supplementary_budget) as supplement 
			from `tabBudget` b, `tabBudget Account` ba 
			where b.docstatus = 1 
			and b.name = ba.parent 
			and b.fiscal_year = '""" + str(filters.fiscal_year) + """'
			"""
	if filters.cost_center:
		query += " and b.cost_center = \'" + str(filters.cost_center) + "\' "
	if filters.business_activity:
		query += " and b.business_activity = \'" + str(filters.business_activity) + "\' "
	if filters.group_by_account:
		query += " group by ba.account"
	else:
		query += " group by ba.account, b.cost_center, b.business_activity"
	return query

def validate_filters(filters):
	if not filters.fiscal_year:
		frappe.throw(_("Fiscal Year {0} is required").format(filters.fiscal_year))

	fiscal_year = frappe.db.get_value("Fiscal Year", filters.fiscal_year, ["year_start_date", "year_end_date"], as_dict=True)
	if not fiscal_year:
		frappe.throw(_("Fiscal Year {0} does not exist").format(filters.fiscal_year))
	else:
		filters.year_start_date = getdate(fiscal_year.year_start_date)
		filters.year_end_date = getdate(fiscal_year.year_end_date)

	if not filters.from_date:
		filters.from_date = filters.year_start_date

	if not filters.to_date:
		filters.to_date = filters.year_end_date

	filters.from_date = getdate(filters.from_date)
	filters.to_date = getdate(filters.to_date)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

	if (filters.from_date < filters.year_start_date) or (filters.from_date > filters.year_end_date):
		frappe.msgprint(_("From Date should be within the Fiscal Year. Assuming From Date = {0}")\
			.format(formatdate(filters.year_start_date)))

		filters.from_date = filters.year_start_date

	if (filters.to_date < filters.year_start_date) or (filters.to_date > filters.year_end_date):
		frappe.msgprint(_("To Date should be within the Fiscal Year. Assuming To Date = {0}")\
			.format(formatdate(filters.year_end_date)))
		filters.to_date = filters.year_end_date


def get_columns():
	return [
		{
		  "fieldname": "account",
		  "label": "Account Head",
		  "fieldtype": "Link",
		  "options": "Account",
		  "width": 200
		},
		{
		  "fieldname": "cost_center",
		  "label": "Cost Center",
		  "fieldtype": "Link",
		  "options": "Cost Center",
		  "width": 130
		},
		{
		  "fieldname": "business_activity",
		  "label": "Business Activity",
		  "fieldtype": "Link",
		  "options": "Business Activity",
		  "width": 130
		},
		{
		  "fieldname": "initial",
		  "label": "Initial Budget",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "supplementary",
		  "label": "Supplementary Budget",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "adjustment_add",
		  "label": "Budget Added",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "adjustment_sent",
		  "label": "Budget Sent",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "adjustment",
		  "label": "Budget Adjustment",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "committed",
		  "label": "Committed Budget",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "consumed",
		  "label": "Consumed Budget",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "available",
		  "label": "Available Budget",
		  "fieldtype": "Currency",
		  "width": 130
		}
	]
