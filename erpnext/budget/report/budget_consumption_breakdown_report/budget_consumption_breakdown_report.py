# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()

	return columns, data

def get_data(filters):
	query = "SELECT account, cost_center, po_no,po_date,amount FROM `tabConsumed Budget` WHERE docstatus = 1 and po_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"
	
	if filters.account:
		query+= "AND account = \'" + str(filters.account) + "\'"
	
	if filters.cost_center:
		query+= " AND cost_center = \'" + str(filters.cost_center) +"\'"

	data = frappe.db.sql(query, as_dict=True)


	return data

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
		  "label": "Document Type",
		  "fieldtype": "Link",
		  "options": "Purchase Invoice",
		  "width": 150
		},
		{
		  "fieldname": "po_date",
		  "label": "Consumed Date",
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

