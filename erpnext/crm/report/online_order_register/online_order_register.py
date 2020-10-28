# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

#####################Created by Cheten Tshering on 27/07/2020 ###########################################
from __future__ import unicode_literals
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt, cstr
import frappe
from frappe import _
import collections

def execute(filters=None):
	if filters.get("report_type") == "Monthly Summary":
		columns = get_monthly_summary_columns(filters)
		data = get_monthly_summary_data(filters)
	else:
		columns = get_columns(filters)
		data = get_data(filters)
	return columns, data

def get_data(filters):
	cond = get_conditions(filters)
	data = 	"""
				select 
					customer.name as order_no, 
					customer.posting_date as order_date, 
					customer.user as customer, 
					customer.full_name,
					ua.mobile_no,
					ua.alternate_mobile_no,
					customer.site,
 					customer.site_type, 
					customer.item, 
					customer.item_name, 
					customer.branch, 
					customer.location, 
					customer.transport_mode, 
					customer.total_quantity,
	  				customer.item_rate, 
					customer.total_item_rate,
					customer.total_transportation_rate,
					customer.total_payable_amount,
	  				customer.total_paid_amount,
					customer.total_balance_amount, 
					customer.sales_order,
					customer.selling_price, 
	  				customer.transportation_rate,
					customer.dzongkhag
				from `tabCustomer Order` as customer 
					left join `tabUser Account` as ua on customer.user = ua.cid 
				where customer.docstatus = 1 and
					DATE(posting_date) between '{from_date}' and '{to_date}'
				{condition} 
			""".format(
                from_date = filters.from_date,
                to_date = filters.to_date,
				condition = cond)
	return frappe.db.sql(data)

def get_conditions(filters):
	cond = ""
	if filters.dzongkhag:
		cond += """ and dzongkhag = "{}" """.format(filters.dzongkhag)
	if filters.branch:
		cond += """and branch = "{}" """.format(filters.branch)
	return cond

def get_monthly_summary_columns(filters):
	columns = [
		{
			"fieldname": "dzongkhag",
			"label": "Dzongkhag",
			"fieldtype": "Link",
			"options": "Dzongkhags",
			"width": 120
		},
	]
	months = frappe.db.sql("""
		SELECT 
			MONTHNAME(posting_date)
		FROM 
			`tabCustomer Order` 
		WHERE 
			year(posting_date) = {fiscal_year}
		GROUP BY 
			MONTHNAME(posting_date)
		ORDER BY
			MONTH(posting_date)
		""".format(
				fiscal_year = filters.get("fiscal_year")
			)
		)

	for month in months:
		temp_data= {
			"fieldname" : month, 
			"label" : month, 
			"fieldtype" : "Float",
			"width" : 150
			}
	
		columns.append(temp_data)

	return columns

def get_monthly_summary_data(filters):
	cond = get_conditions(filters)
	sql = """
		SELECT 
			customer.dzongkhag,
			SUM(IF(month(customer.posting_date) = 1,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 2,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 3,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 4,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 5,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 6,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 7,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 8,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 9,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 10,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 11,customer.total_quantity,0)),
			SUM(IF(month(customer.posting_date) = 12,customer.total_quantity,0)) 
		FROM
			`tabCustomer Order` as customer 
		WHERE 
			year(customer.posting_date) = {fiscal_year}
			{conditions}
		GROUP BY 
			customer.dzongkhag
		""".format(
				fiscal_year = filters.get("fiscal_year"), 
				conditions = cond
			)
	return frappe.db.sql(sql)

def get_columns(filters):
	columns = [
				   _("Order Number") + ":Link/Customer Order:100", 
				   _("Order Date") + ":Date Time:100", 
				   _("Customer ID") + ":Link/Customer:140",
				   _("Customer Name") + ":Data:100",
				   _("Mobile Number") + ":Data:100", 
				   _("Alternate Mobile Number") + ":Data:100", 
				   _("Site ID") + ":Link/Site:120", 
				   _("Site Type") + ":Link/Site Type:120",
				   _("Item Code") + ":Link/Item:120",  
				   _("Item Name") + ":Data:100", 
				   _("Source Branch") + ":Link/Branch:120", 
				   _("Source Location") + ":Link/Location:120",
				   _("Transport Mode") + ":Data:120", 
				   _("Order Quantity") + ":Float:120", 
				   _("Item Rate") + ":Data:120", 
				   _("Total Item Rate") + ":Currency:120", 
				   _("Total Transportation Rate") + ":Currency:120", 
				   _("Total Payable Amount") + ":Currency: 100", 
				   _("Total Paid Amount") + ":Currency:100", 
				   _("Balance Payable Amount") + ":Currency:100",
				   _("Sales Order") + ":Link/Sales Order:120", 
				   _("Selling Price Reference") + ":Link/Selling Price:120",
				   _("Transportation Rate Reference") + ":Link/Transportation Rate:120",  
				   _("Dzongkhag") + ":Link/Dzongkhags:120"
				]
	return columns
	
	
