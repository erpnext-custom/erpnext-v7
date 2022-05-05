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
		row = [d.name, d.posting_date, d.cheque_no, d.cheque_date, d.total_amount, d.pay_to_recd_from, d.cheque_status, d.cancelled_amount]
		data.append(row);

	return data

def construct_query(filters=None):
	je_branch_cond = ""
	pe_branch_cond = ""
	dp_branch_cond = ""
	pd_branch_cond = ""
	mp_branch_cond = ""
	tds_branch_cond = ""
	je_posting_date = "AND je.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"
	pe_posting_date = "AND pe.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"
	dp_posting_date = "dp.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"
	pd_posting_date = "pd.entry_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"
	mp_posting_date = "mp.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"
	tds_posting_date = "tr.posting_date BETWEEN \'" + str(filters.from_date) + "\' AND \'" + str(filters.to_date) + "\'"
     
	if filters.branch != None:
		je_branch_cond += "AND je.branch = \'"+str(filters.branch)+"\'"
		pe_branch_cond += "AND pe.branch = \'"+str(filters.branch)+"\'"
		dp_branch_cond += "AND dp.branch = \'"+str(filters.branch)+"\'"
		pd_branch_cond += "AND pd.branch = \'"+str(filters.branch)+"\'"
		mp_branch_cond += "AND mp.branch = \'"+str(filters.branch)+"\'"
		tds_branch_cond += "AND tr.branch = \'"+str(filters.branch)+"\'"
  
	query = """
		SELECT 
			je.name, je.posting_date, je.cheque_no, je.cheque_date, 
			CASE je.docstatus WHEN 2 THEN 0 ELSE je.total_amount END AS total_amount, 
			CASE je.docstatus WHEN 2 THEN je.total_amount ELSE 0 END AS cancelled_amount, 
			je.pay_to_recd_from, 
			CASE je.docstatus WHEN 2 THEN \"CANCELLED\" ELSE null END AS cheque_status 
		FROM `tabJournal Entry` je 
		WHERE je.naming_series IN ('Bank Payment Voucher') AND NOT isnull(je.cheque_no) {0} {1} AND 
		NOT EXISTS (SELECT 1 from `tabJournal Entry` je1 where je1.amended_from = je.name) 
		
		UNION ALL 

		SELECT 
			pe.name, pe.posting_date, pe.reference_no AS cheque_no, pe.reference_date AS cheque_date, 
			CASE pe.docstatus 
				WHEN 2 THEN 0 
				ELSE (CASE WHEN pe.base_paid_amount > 0 THEN pe.base_paid_amount ELSE pe.base_received_amount END) 
			END AS total_amount, 
			CASE pe.docstatus 
				WHEN 2 THEN (CASE WHEN pe.base_paid_amount > 0 THEN pe.base_paid_amount ELSE pe.base_received_amount END)
				ELSE 0 
			END AS cancelled_amount, 
			pe.pay_to_recd_from, 
			CASE pe.docstatus 
				WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabPayment Entry` pe 
		WHERE pe.naming_series IN ('Bank Payment Voucher') AND NOT isnull(pe.reference_no) {2} {3} AND 
		NOT EXISTS (SELECT 1 from `tabPayment Entry` pe1 where pe1.amended_from = pe.name) 
		UNION ALL 
		
		SELECT 
			dp.name, dp.posting_date, dp.cheque_no AS cheque_no, dp.cheque_date AS cheque_date, 
			CASE dp.docstatus WHEN 2 THEN 0 ELSE dp.net_amount END AS total_amount, 
			CASE dp.docstatus WHEN 2 THEN dp.net_amount ELSE 0 END AS cancelled_amount, 
			dp.pay_to_recd_from, 
			CASE dp.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabDirect Payment` dp where {4} {5} AND 
		NOT EXISTS (SELECT 1 from `tabDirect Payment` dp1 where dp1.amended_from = dp.name)
		AND dp.credit_account IN (
						SELECT name 
						FROM `tabAccount` 
						WHERE account_type = 'Bank')
		UNION ALL

		SELECT 
			pd.name, pd.entry_date, pd.cheque_no, pd.cheque_date, 
            CASE pd.docstatus WHEN 2 THEN 0 ELSE pd.amount END AS total_amount, 
			CASE pd.docstatus WHEN 2 THEN pd.amount ELSE 0 END AS cancelled_amount, 
			pd.pay_to_recd_from, 
			CASE pd.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabPol Advance` pd  
		WHERE 
		{6} {7} AND 
		NOT EXISTS (SELECT 1 from `tabPol Advance` pd1 where pd1.amended_from = pd.name)
		AND pd.name IN (
					SELECT gl.voucher_no 
					FROM `tabGL Entry` gl 
					WHERE voucher_no LIKE 'POLAD21%' AND gl.account IN (
						SELECT name 
						FROM `tabAccount` 
						WHERE account_type = 'Bank'))
		UNION ALL 
		
		SELECT 
			mp.name, mp.posting_date, mp.cheque_no, mp.cheque_date, 
			CASE mp.docstatus WHEN 2 THEN 0 ELSE mp.net_amount END AS total_amount, 
			CASE mp.docstatus WHEN 2 THEN mp.net_amount ELSE 0 END AS cancelled_amount, 
			mp.pay_to_recd_from, 
			CASE mp.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabMechanical Payment` mp where {8} {9} AND 
		NOT EXISTS (SELECT 1 from `tabMechanical Payment` mp1 where mp1.amended_from = mp.name)
		AND mp.outgoing_account IN (
						SELECT name 
						FROM `tabAccount` 
						WHERE account_type = 'Bank')
		UNION ALL

		SELECT 
			tr.name, tr.posting_date, tr.cheque_no, tr.cheque_date, 
            CASE tr.docstatus WHEN 2 THEN 0 ELSE tr.total_amount END AS total_amount, 
			CASE tr.docstatus WHEN 2 THEN tr.total_amount ELSE 0 END AS cancelled_amount, 
			tr.pay_to_recd_from, 
			CASE tr.docstatus WHEN 2 THEN 'CANCELLED' ELSE null END AS cheque_status 
		FROM `tabTDS Remittance` tr  
		WHERE 
		{10} {11} AND 
		NOT EXISTS (SELECT 1 from `tabTDS Remittance` tr1 where tr1.amended_from = tr.name)
		AND tr.account IN (
						SELECT name 
						FROM `tabAccount` 
						WHERE account_type = 'Bank')
	""".format(je_posting_date, je_branch_cond, pe_posting_date, pe_branch_cond, dp_posting_date, dp_branch_cond, pd_posting_date, pd_branch_cond, mp_posting_date, mp_branch_cond, tds_posting_date, tds_branch_cond)

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
		  "fieldname": "voucher_no",
		  "label": "Voucher No",
		  "fieldtype": "Data",
		  "width": 150
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
		  "fieldname": "receipant",
		  "label": "Receipant",
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
		  "fieldname": "canaelled_amount",
		  "label": "Cancelled Amount",
		  "fieldtype": "Currency",
		  "width": 130
		},
	]
