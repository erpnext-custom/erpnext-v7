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
	
	for d in datas:
		adjustment = flt(d.added) - flt(d.deducted)
		available = flt(d.initial_budget) + flt(adjustment) + flt(d.supplement) - flt(d.consumed)
		row = {
			"account": d.account, 
			"cost_center": d.cost_center,
			"initial": d.initial_budget,
			"supplementary": d.supplement,
			"adjustment": adjustment,
			"consumed": d.consumed,
			"available": available
		}
		data.append(row);

	return data

def construct_query(filters=None):
	query = "select b.cost_center, ba.account, ba.budget_amount, ba.initial_budget,(select SUM(amount) from `tabReappropriation Details` rd where rd.from_cost_center = b.cost_center and rd.from_account = ba.account and rd.appropriation_on BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as deducted,  (select SUM(amount) from `tabReappropriation Details` rd where rd.to_cost_center = b.cost_center and rd.to_account = ba.account and rd.appropriation_on BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as added, (select SUM(amount) from `tabSupplementary Details` rd where rd.to_cc = b.cost_center and rd.to_acc = ba.account and rd.posted_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\') as supplement, (select SUM(gl.debit - gl.credit) as consumed from `tabGL Entry` gl where gl.account = ba.account and gl.cost_center = b.cost_center and gl.docstatus = 1 and gl.posting_date  BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' ) as consumed from `tabBudget` b, `tabBudget Account` ba where b.docstatus = 1 and b.name = ba.parent and b.fiscal_year = " + str(filters.fiscal_year)
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
		  "width": 200
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
