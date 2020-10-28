# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):

	if filters.get("report_type") == "Register":
		columns = get_register_columns(filters) 
		data = get_register_data(filters)

	else: 
		columns = get_monthly_summary_columns(filters)
		data = get_monthly_summary_data(filters)
	
	return columns, data

def get_monthly_summary_columns(filters=None):
	data=[{
		"fieldname" : "dzongkhags", 
		"label" : 'Dzongkhag', 
		"fieldtype" : "Link",
		"options": "Dzongkhags",
		"width" : 100
	}]
	months = frappe.db.sql_list("""
		SELECT 
			MONTHNAME(transaction_time)
		FROM 
			`tabOnline Payment` 
		WHERE 
			year(transaction_time) = {fiscal_year}
		GROUP BY 
			MONTHNAME(transaction_time)
		ORDER BY
			MONTH(transaction_time)
		""".format(
				fiscal_year = filters.get("fiscal_year")
			)
		)
	month_lst = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'Sepetember', 'October', 'November', 'December']
	for info in month_lst:
		temp_data= {
			"fieldname" : info, 
			"label" : info, 
			"fieldtype" : "Currency",
			"width" : 130,
			"hidden": 0 if info in months else 1 
		}
		data.append(temp_data)	
	return (data)

def get_monthly_summary_data(filters=None):
	cond = get_conditions(filters)
	sql = """
		SELECT 
			customer.dzongkhag,
			SUM(IF(month(online_payment.transaction_time) = 1,online_payment.amount,0)) January,
			SUM(IF(month(online_payment.transaction_time) = 2,online_payment.amount,0)) February,
			SUM(IF(month(online_payment.transaction_time) = 3,online_payment.amount,0)) March,
			SUM(IF(month(online_payment.transaction_time) = 4,online_payment.amount,0)) April,
			SUM(IF(month(online_payment.transaction_time) = 5,online_payment.amount,0)) May,
			SUM(IF(month(online_payment.transaction_time) = 6,online_payment.amount,0)) June,
			SUM(IF(month(online_payment.transaction_time) = 7,online_payment.amount,0)) July,
			SUM(IF(month(online_payment.transaction_time) = 8,online_payment.amount,0)) August,
			SUM(IF(month(online_payment.transaction_time) = 9,online_payment.amount,0)) September,
			SUM(IF(month(online_payment.transaction_time) = 10,online_payment.amount,0)) October,
			SUM(IF(month(online_payment.transaction_time) = 11,online_payment.amount,0)) November,
			SUM(IF(month(online_payment.transaction_time) = 12,online_payment.amount,0)) December
		FROM
			`tabOnline Payment` as online_payment 
		JOIN
			`tabCustomer Order` as customer 
		ON 
			online_payment.customer_order = customer.name
		WHERE 
			year(online_payment.transaction_time) = {fiscal_year}
		AND online_payment.status = 'Successful'
		{conditions}

		GROUP BY 
			customer.dzongkhag
		""".format(
				fiscal_year = filters.get("fiscal_year"), 
				conditions = cond
			)
	return frappe.db.sql(sql)


def get_register_columns(filters=None): 
	columns = [
		{
		  	"fieldname": "customer_name",
		  	"label": "Customer Name",
		  	"fieldtype": "Link",
			"options":"Customer",
		  	"width": 130
		},
		{
		  	"fieldname": "dzongkhag",
		  	"label": "Dzongkhag",
		  	"fieldtype": "Link",
			"options":"Dzongkhags",
		  	"width": 90
		},
		{
		  	"fieldname": "site",
		  	"label": "Site",
		  	"fieldtype": "Link",
			"options":"Site",
		  	"width": 100
		},
		{
			
		  	"fieldname": "bank_name",
		  	"label": "Bank Name",
		  	"fieldtype": "Data",
		  	"width": 80
		},
		{
		  	"fieldname": "bank_account",
		  	"label": "Bank Account",
		  	"fieldtype": "Data",
		  	"width": 100
		},
		{
		  	"fieldname": "amount",
		  	"label": "Amount",
		  	"fieldtype": "Currency",
		  	"width": 100
		},
		{
		  	"fieldname": "payment_id",
		  	"label": "Payment Id",
		  	"fieldtype": "Link",
			"options": "Online Payment",
		  	"width": 130
		},
		{
		  	"fieldname": "bfs_trans_id",
		  	"label": "BFS Trans Id",
		  	"fieldtype": "Data",
		  	"width": 100
		},
		{
		  	"fieldname": "bfs_trans_time",
		  	"label": "BFS Trans Time",
		  	"fieldtype": "Datetime",
		  	"width": 160
		},
		{
		  	"fieldname": "status",
		  	"label": "Status",
		  	"fieldtype": "Data",
			"width" : 80
		},
		{
		  	"fieldname": "customer_order",
		  	"label": "Customer Order",
		  	"fieldtype": "Link",
			"options" : "Customer Order",
		  	"width": 130
		},
	]
	return columns


def get_register_data(filters=None): 
	cond = get_conditions(filters)
	payment_info = """ 
		SELECT 
			customer.customer as customer_name,
			customer.dzongkhag as dzongkhag, 
			customer.site as site, 
			fin_ins.name as bank_name,
			online_payment.bank_account as bank_account, 
			online_payment.amount as amount,
			online_payment.name as payment_id, 
			online_payment.transaction_id as bfs_trans_id, 
			online_payment.transaction_time as bfs_trans_time, 
			online_payment.status as status, 
			online_payment.customer_order as customer_order
			
		FROM 
			`tabOnline Payment` as online_payment 
		JOIN 
			`tabFinancial Institution` as fin_ins 
		ON 
			online_payment.bank_code = fin_ins.bank_code
		JOIN 
			`tabCustomer Order` as customer 
		ON 
			online_payment.customer_order = customer.name
		WHERE 
			DATE(online_payment.transaction_time) between '{from_date}' and '{to_date}' 
			{conditions} 
		""".format(
				from_date=filters.get("from_date"), 
				to_date=filters.get("to_date"),
				conditions = cond 
			)
	return frappe.db.sql(payment_info)


def get_conditions(filters):
	conditions=""
	if filters.get("report_type") == "Register": 
		if filters.get("status") and filters.get("status") != "All": 
			conditions += """ and online_payment.status = "{}" """.format(filters.get("status"))

	if filters.get("dzongkhag"):
		conditions += """ and customer.dzongkhag = "{}" """.format(filters.get("dzongkhag"))

	return conditions


