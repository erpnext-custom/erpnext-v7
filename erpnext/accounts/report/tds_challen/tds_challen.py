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
	data = get_data(queries, filters);

	return columns, data

def get_data(query, filters):
	data = []
	data1 = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		status = 'Not Paid'
		bil = frappe.db.sql(""" select name from `tabRRCO Receipt Entries` where bill_no = '{0}' and docstatus =1""".format(d.bill_no), as_dict = 1)
		if bil:
			status = 'Paid'
		if filters.get("cost_center") and d.cost_center == filters.get("cost_center"):
			row = [d.name, d.vendor_tpn_no, d.bill_no, d.bill_date, d.tds_taxable_amount, d.tds_rate, d.tds_amount, d.cost_center, status]
			data.append(row);
		else:
			row = [d.name, d.vendor_tpn_no, d.bill_no, d.bill_date, d.tds_taxable_amount, d.tds_rate, d.tds_amount, d.cost_center, status]
			data1.append(row);
	if filters.get("cost_center"):
		return data
	else:
		return data1

def construct_query(filters=None):
	if not filters.tds_rate:
		filters.tds_rate = '2'
	pi_cost_center = "1 = 1"
      	dp_cost_center = "1 = 1"

	if filters.get("cost_center"):
		pi_cost_center = "p.tds_cost_center = '{0}'".format(filters.get("cost_center"))
		dp_cost_center = "d.cost_center = '{0}'".format(filters.get("cost_center"))
	query = " SELECT s.vendor_tpn_no, s.name, p.bill_no, p.bill_date, p.tds_taxable_amount, p.tds_rate, p.tds_amount, p.tds_cost_center as cost_center  FROM `tabPurchase Invoice` as p, `tabSupplier` as s WHERE p.docstatus = 1 and p.supplier = s.name AND p.tds_amount > 0 AND p.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\' AND p.tds_rate = " + filters.tds_rate + " UNION SELECT ss.vendor_tpn_no, ss.name, d.name as bill_no, d.posting_date as bill_date, d.amount as tds_taxable_amount, d.tds_percent as tds_rate, d.tds_amount, d.cost_center as cost_center FROM `tabDirect Payment` as d, `tabSupplier` as ss WHERE d.docstatus = 1 and d.supplier = ss.name AND d.tds_amount > 0 AND d.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'  AND d.tds_percent = " + filters.tds_rate + ""
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
		  "fieldname": "vendor_name",
		  "label": "Vendor Name",
		  "fieldtype": "Data",
		  "width": 250
		},
		{
		  "fieldname": "tpn_no",
		  "label": "TPN Number",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "invoice_no",
		  "label": "Invoice No",
		  "fieldtype": "Data",
		  "width": 200
		},
		{
		  "fieldname": "Invoice_date",
		  "label": "Invoice Date",
		  "fieldtype": "Date",
		  "width": 100
		},
		{
		  "fieldname": "bill_amount",
		  "label": "Bill Amount",
		  "fieldtype": "Currency",
		  "width": 150
		},
		{
		  "fieldname": "tds_rate",
		  "label": "TDS Rate(%)",
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
	  	"fieldname": "cost_center",
	   	"label": "Cost Center",
	      	"fieldtype": "Link",
		"options": "Cost Centr",
		"width": 150
		},
		{
		"fieldname": "status",
		"label": "Status",
		"fieldtype": "Data",
		"width": 100
		},
	
		        
	]
