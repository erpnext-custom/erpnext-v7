# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters=None): 
	conditions = get_conditions(filters)
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
			online_payment.transaction_time between '{from_date}' and '{to_date}' 
			{cond} 
		""".format(
				from_date=filters.get("from_date"), 
				to_date=filters.get("to_date"),
				cond = conditions 
			)

	return frappe.db.sql(payment_info)

def get_columns(filters=None): 
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
			"options": "Customer Order",
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
		  	"fieldtype": "Data",
		  	"width": 130
		},
	]
	return columns

def get_conditions(filters):
	cond=""
	if filters.get("dzongkhag"):
		cond += """ and customer.dzongkhag = "{}" """.format(filters.get("dzongkhag"))

	if filters.get("status") and filters.get("status") != "All": 
		cond += """ and online_payment.status = "{}" """.format(filters.get("status"))
	return cond

