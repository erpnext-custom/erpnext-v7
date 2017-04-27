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
		row = {
			"account": d.account, 
			"cost_center": d.cost_center,
			"po_no": d.po_no,
			"po_date": d.po_date,
			"amount": d.amount
		}
		data.append(row);
	return data

def construct_query(filters=None):
	query = "SELECT distinct com.account,com.cost_center,com.po_no,com.po_date,com.amount FROM `tabCommitted Budget` com WHERE com.docstatus = 1 and com.po_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' and not exists (select 1 from `tabConsumed Budget` cb where cb.account = com.account and cb.cost_center = com.cost_center and cb.com_ref = com.po_no and (IFNULL(com.item_code,1) = 1 OR cb.item_code = com.item_code)) "
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
		  "width": 250
		},
		{
		  "fieldname": "cost_center",
		  "label": "Cost Center",
		  "fieldtype": "Link",
		  "options": "Cost Center",
		  "width": 250
		},
		{
		  "fieldname": "po_no",
		  "label": "Purchase Order",
		  "fieldtype": "Link",
		  "options": "Purchase Order",
		  "width": 150
		},
		{
		  "fieldname": "po_date",
		  "label": "Commit Date",
		  "fieldtype": "Date",
		  "width": 100
		},
		{
		  "fieldname": "amount",
		  "label": "Amount",
		  "fieldtype": "Currency",
		  "width": 130
		}
	]
