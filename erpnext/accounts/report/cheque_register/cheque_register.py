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
		row = [d.name, d.posting_date, d.cheque_no, d.cheque_date, d.total_amount, d.pay_to_recd_from]
		data.append(row);
	
	return data

def construct_query(filters=None):
	query = "SELECT name, posting_date, cheque_no, cheque_date, total_amount, pay_to_recd_from FROM `tabJournal Entry` WHERE voucher_type = \"Bank Entry\" AND NOT isnull(cheque_no) AND posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\';";

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
		  "fieldname": "voucher_no",
		  "label": "Voucher No",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
		  "fieldname": "voucher_date",
		  "label": "Voucher Date",
		  "fieldtype": "Date",
		  "width": 120
		},
		{
		  "fieldname": "cheque_no",
		  "label": "Cheque No",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "cheque_date",
		  "label": "Cheque Date",
		  "fieldtype": "Date",
		  "width": 120
		},
		{
		  "fieldname": "amount",
		  "label": "Amount",
		  "fieldtype": "Currency",
		  "width": 180
		},
		{
		  "fieldname": "receipant",
		  "label": "Receipant",
		  "fieldtype": "Data",
		  "width": 230
		},
	]
