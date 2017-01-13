# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	validate_filters(filters);
	columns = get_columns();
	queries = construct_query(filters);
	data = get_data(queries);

	return columns, data

def get_data(query):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	ini = su = cm = co = ad = av = 0
	for d in datas:
		adjustment = flt(d.added) - flt(d.deducted)
		consumed = flt(d.consumed)
		supplement = flt(d.supplement)
		committed = flt(d.committed)
		#frappe.msgprint("B: " + str(committed))
		if committed > 0:
			committed-=consumed
		#frappe.msgprint("A: " + str(committed))

		available = flt(d.initial_budget) + flt(adjustment) + flt(d.supplement) - consumed - committed
		row = {
			"account": d.account, 
			"cost_center": d.cost_center,
			"initial": flt(d.initial_budget),
			"supplementary": supplement,
			"adjustment": adjustment,
			"committed": committed,
			"consumed": consumed,
			"available": available
		}
		data.append(row);
		ini+=flt(d.initial_budget)
		su+=supplement
		cm+=committed
		co+=consumed
		ad+=adjustment
		av+=available

	row = {
		"account": "Total",
		"cost_center": "",
		"initial": ini,
		"supplementary": su,
		"adjustment": ad,
		"committed": cm,
		"consumed": co,
		"available": av
	}
	data.append(row)

	return data

def construct_query(filters=None):
	#query = "select b.cost_center, ba.account, ba.budget_amount, ba.initial_budget,(select SUM(amount) from `tabReappropriation Details` rd where rd.from_cost_center = b.cost_center and rd.from_account = ba.account and rd.appropriation_on BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as deducted, (select SUM(amount) from `tabConsumed Budget` cb where cb.cost_center = b.cost_center and cb.account = ba.account and cb.date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as committed, (select SUM(amount) from `tabReappropriation Details` rd where rd.to_cost_center = b.cost_center and rd.to_account = ba.account and rd.appropriation_on BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as added, (select SUM(amount) from `tabSupplementary Details` rd where rd.to_cc = b.cost_center and rd.to_acc = ba.account and rd.posted_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\') as supplement, (select SUM(gl.debit - gl.credit) as consumed from `tabGL Entry` gl where gl.account = ba.account and gl.cost_center = b.cost_center and gl.docstatus = 1 and gl.is_opening != \'Yes\' and gl.posting_date  BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as consumed from `tabBudget` b, `tabBudget Account` ba where b.docstatus = 1 and b.name = ba.parent and b.fiscal_year = " + str(filters.fiscal_year)

	query = "select b.cost_center, ba.account, ba.budget_amount, ba.initial_budget, ba.budget_received as added, ba.budget_sent as deducted, ba.supplementary_budget as supplement, (select SUM(amount) from `tabConsumed Budget` cb where cb.cost_center = b.cost_center and cb.account = ba.account and cb.po_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' and EXISTS (SELECT 1 FROM `tabJournal Entry` a WHERE a.name = cb.po_no AND a.docstatus = 1 UNION SELECT 1 FROM `tabPurchase Order` po WHERE po.name = cb.po_no AND po.docstatus = 1)) as committed, (select SUM(gl.debit - gl.credit) as consumed from `tabGL Entry` gl where gl.account = ba.account and gl.cost_center = b.cost_center and gl.docstatus = 1 and gl.is_opening != \'Yes\' and gl.posting_date  BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' and gl.voucher_type != 'Stock Entry' ) as consumed from `tabBudget` b, `tabBudget Account` ba where b.docstatus = 1 and b.name = ba.parent and b.fiscal_year = " + str(filters.fiscal_year)
	#query = "select b.cost_center, ba.account, ba.budget_amount, ba.initial_budget, ba.budget_received as added, ba.budget_sent as deducted, ba.supplementary_budget as supplement, (select SUM(amount) from `tabConsumed Budget` cb where cb.cost_center = b.cost_center and cb.account = ba.account and cb.date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as committed, (select SUM(gl.debit - gl.credit) as consumed from `tabGL Entry` gl where gl.account = ba.account and gl.cost_center = b.cost_center and gl.docstatus = 1 and gl.is_opening != \'Yes\' and gl.posting_date  BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as consumed from `tabBudget` b, `tabBudget Account` ba where b.docstatus = 1 and b.name = ba.parent and b.fiscal_year = " + str(filters.fiscal_year)
	return query;

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
