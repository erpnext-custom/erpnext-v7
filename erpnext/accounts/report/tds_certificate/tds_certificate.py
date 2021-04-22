# For license information, please see license.txt
# Frappe Technologiss Pvt. Ltd. and contributors
	
from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data
	
def get_columns():
	return [
		("Invoice Date") + ":Date:120",
		("Gross Amount") + ":Currency:120",
		("tds_rate") + ":Data:80",
		("TDS Amount") + ":Currency:100",
		("Cheque Number") + ":Data:100",
		("Cheque Date") + ":Date:80",
		("Receipt Number") + ":Data:100",
		("Receipt Date") + ":Date:100",
		("Branch") + ":Link/Branch:120"
	]

def get_data(filters):
	query = """SELECT a.posting_date, a.tds_taxable_amount, a.tds_rate, a.tds_amount, b.cheque_number, b.cheque_date, 
		b.receipt_number, b.receipt_date, b.branch 
		FROM `tabPurchase Invoice` AS a, `tabRRCO Receipt Entries` AS b 
		WHERE a.name = b.purchase_invoice 
		AND a.posting_date BETWEEN '{0}' AND '{1}'
		AND a.supplier = '{2}' 
		UNION 
		SELECT  
			d.posting_date,  
			if(d.single_party_multiple_payments = 1, d.taxable_amount, di.taxable_amount) as tds_taxable_amount, d.tds_percent as tds_rate,  
			if(d.single_party_multiple_payments = 1, d.tds_amount, di.tds_amount) as tds_amount, 
			rr.cheque_number,  rr.cheque_date, rr.receipt_number, rr.receipt_date, rr.branch 
		FROM 
			`tabDirect Payment` AS d
		INNER JOIN
			`tabRRCO Receipt Entries` AS rr ON rr.purchase_invoice = d.name 
		LEFT JOIN 
			`tabDirect Payment Item` AS di ON di.parent = d.name 
		WHERE d.posting_date BETWEEN '{0}' AND '{1}'
		AND (
			(d.single_party_multiple_payments = 1 AND d.party = '{2}')
			OR
			(d.single_party_multiple_payments = 0 AND  di.party = '{2}')
		)""".format(filters.from_date, filters.to_date, filters.vendor_name)
	return frappe.db.sql(query)
