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
		row = [d.posting_date, round(flt(d.tds_taxable_amount,2),2), d.tds_rate, d.tds_amount, d.cheque_number, d.cheque_date, d.receipt_number, d.receipt_date]
		data.append(row);
	
	return data

def construct_query(filters=None):
	if not filters.vendor_name:
		filters.vendor_name = ""
	if not filters.branch:
		filters.branch = "27492yreuwhroi210e"

	query = "SELECT a.posting_date, a.tds_taxable_amount, a.tds_rate, a.tds_amount, b.cheque_number, b.cheque_date, b.receipt_number, b.receipt_date FROM `tabPurchase Invoice` AS a, `tabRRCO Receipt Entries` AS b WHERE a.name = b.purchase_invoice AND a.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' AND a.supplier = \'" + filters.vendor_name + "\' UNION SELECT d.posting_date, d.amount as tds_taxable_amount, d.tds_percent as tds_rate, d.tds_amount, rr.cheque_number, rr.cheque_date, rr.receipt_number, rr.receipt_date FROM `tabDirect Payment` AS d, `tabRRCO Receipt Entries` AS rr WHERE d.name = rr.purchase_invoice AND d.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' AND d.party = \'" + filters.vendor_name + "\'"
	
	query+=";";
	
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
		  "fieldname": "invoice_date",
		  "label": "Month & Date",
		  "fieldtype": "Date",
		  "width": 100
		},
		{
		  "fieldname": "tds_taxable_amount",
		  "label": "Gross Amount",
		  "fieldtype": "Currency",
		  "width": 150
		},
		{
		  "fieldname": "tds_rate",
		  "label": "TDS Rate",
		  "fieldtype": "Data",
		  "width": 90
		},
		{
		  "fieldname": "tds_amount",
		  "label": "TDS Amount",
		  "fieldtype": "Currency",
		  "width": 150
		},
		{
		  "fieldname": "cheque_number",
		  "label": "Cheque Number",
		  "fieldtype": "Data",
		  "width": 120
		},
		{
		  "fieldname": "cheque_date",
		  "label": "Cheque Date",
		  "fieldtype": "Date",
		  "width": 100
		},
		{
		  "fieldname": "receipt_number",
		  "label": "Receipt Number",
		  "fieldtype": "Data",
		  "width": 150
		},
		{
		  "fieldname": "receipt_date",
		  "label": "Receipt Date",
		  "fieldtype": "Date",
		  "width": 100
		},
	]
