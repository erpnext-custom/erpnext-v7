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
	total = {}
	total_amount = 0
	total_cancelled = 0
	for d in datas:
		key = (d.cheque_no, d.cheque_date)
		total[key] = flt(total.get(key)) + flt(d.amount)

	for d in datas:
		key = (d.cheque_no, d.cheque_date)
		row = [d.voucher_type, d.voucher_no, d.voucher_date, d.cheque_no, d.cheque_date, d.amount, total[key],
			d.recipient, d.cheque_status, d.cancelled_amount]
		data.append(row)
		total_amount += flt(d.amount)
		total_cancelled += flt(d.cancelled_amount)

	# Total row
	row = ['Total', '', '', '', '', total_amount, '', '', '', total_cancelled]
	data.append(row)

	return data

def construct_query(filters=None):
	query = """SELECT 'Journal Entry' as voucher_type, je.name as voucher_no, je.posting_date as voucher_date, 
			je.cheque_no, je.cheque_date, 
			CASE je.docstatus WHEN 2 THEN 0 ELSE je.total_amount END AS amount, 
			CASE je.docstatus WHEN 2 THEN je.total_amount ELSE 0 END AS cancelled_amount, 
			je.pay_to_recd_from recipient, 
			CASE je.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabJournal Entry` je 
		WHERE je.naming_series IN ('Bank Payment Voucher') 
		AND IFNULL(je.cheque_no,'') != '' 
		AND je.posting_date BETWEEN '{from_date}' AND '{to_date}' 
		AND NOT EXISTS (SELECT 1 from `tabJournal Entry` je1 where je1.amended_from = je.name) 
		UNION ALL 
		SELECT 'Payment Entry' as voucher_type, pe.name as voucher_no, pe.posting_date as voucher_date, 
			pe.reference_no AS cheque_no, pe.reference_date AS cheque_date, 
			CASE pe.docstatus WHEN 2 THEN 0 
				ELSE (CASE WHEN pe.base_paid_amount > 0 THEN pe.base_paid_amount ELSE pe.base_received_amount END) 
			END AS amount, 
			CASE pe.docstatus WHEN 2 THEN (CASE WHEN pe.base_paid_amount > 0 THEN pe.base_paid_amount ELSE pe.base_received_amount END) 
				ELSE 0 
			END AS cancelled_amount, 
			pe.pay_to_recd_from as recipient, 
			CASE pe.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabPayment Entry` pe 
		WHERE pe.naming_series IN ('Bank Payment Voucher') 
		AND IFNULL(pe.reference_no,'') != '' 
		AND pe.posting_date BETWEEN '{from_date}' AND '{to_date}' 
		AND NOT EXISTS (SELECT 1 from `tabPayment Entry` pe1 where pe1.amended_from = pe.name) 
		UNION ALL 
		SELECT 'Transporter Payment' as voucher_type, tp.name as voucher_no, tp.posting_date as voucher_date, 
			tp.cheque_no, tp.cheque_date,
			CASE tp.docstatus WHEN 2 THEN 0 ELSE tp.amount_payable END AS amount, 
			CASE tp.docstatus WHEN 2 THEN tp.amount_payable ELSE 0 END AS cancelled_amount, 
			tp.registration_no as recipient, 
			CASE tp.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabTransporter Payment` tp 
		WHERE IFNULL(tp.cheque_no,'') != '' 
		AND tp.posting_date BETWEEN '{from_date}' AND '{to_date}' 
		AND NOT EXISTS (SELECT 1 from `tabTransporter Payment` tp1 where tp1.amended_from = tp.name) 
		UNION ALL 
		SELECT 'Direct Payment' as voucher_type, dp.name as voucher_no, dp.posting_date as voucher_date, 
			dp.cheque_no, dp.cheque_date, CASE dp.docstatus WHEN 2 THEN 0 ELSE dp.net_amount END AS amount, 
			CASE dp.docstatus WHEN 2 THEN dp.net_amount ELSE 0 END AS cancelled_amount, 
			dp.party as recipient, 
			CASE dp.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabDirect Payment` dp 
		WHERE IFNULL(dp.cheque_no,'') != '' 
		AND dp.posting_date BETWEEN  '{from_date}' AND '{to_date}' 
		AND NOT EXISTS (SELECT 1 from `tabDirect Payment` dp1 where dp1.amended_from = dp.name) 
		UNION ALL 
		SELECT 'EME Payment' as voucher_type, eme.name as voucher_no, eme.posting_date as voucher_date, 
			eme.cheque_no, eme.cheque_date, CASE eme.docstatus WHEN 2 THEN 0 ELSE eme.payable_amount END AS amount, 
			CASE eme.docstatus WHEN 2 THEN eme.payable_amount ELSE 0 END AS cancelled_amount, 
			eme.supplier as recipient, 
			CASE eme.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabEME Payment` as eme 
		WHERE IFNULL(eme.cheque_no,'') != ''
		AND eme.posting_date BETWEEN '{from_date}' AND '{to_date}' 
		AND NOT EXISTS(SELECT 1 from `tabEME Payment` eme1 where eme1.amended_from = eme.name)
		""".format(from_date=filters.from_date, to_date=filters.to_date)
	return query;

def validate_filters(filters):
	'''
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
	'''
	return

def get_columns():
	return [
		{
		  "fieldname": "voucher_type",
		  "label": "Voucher Type",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "voucher_no",
		  "label": "Voucher No",
		  "fieldtype": "Dynamic Link",
		  "options": "voucher_type",
		  "width": 120
		},
		{
		  "fieldname": "voucher_date",
		  "label": "Voucher Date",
		  "fieldtype": "Date",
		  "width": 100
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
		  "width": 100
		},
		{
		  "fieldname": "amount",
		  "label": "Amount",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "total_amount",
		  "label": "Total Amount",
		  "fieldtype": "Currency",
		  "width": 130
		},
		{
		  "fieldname": "recipient",
		  "label": "Recipient",
		  "fieldtype": "Data",
		  "width": 230
		},
		{
		  "fieldname": "cheque_status",
		  "label": "Cheque Status",
		  "fieldtype": "Data",
		  "width": 100
		},
		{
		  "fieldname": "cancelled_amount",
		  "label": "Cancelled Amount",
		  "fieldtype": "Currency",
		  "width": 130
		},
	]
