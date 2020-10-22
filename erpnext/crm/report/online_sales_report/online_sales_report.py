# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	cond = get_conditions(filters)
	data = frappe.db.sql("""
		select s.name site, date(s.creation) as site_date, s.site_type, s.construction_type, 
			s.approval_no, c.name as customer, s.dzongkhag,
			sum(si.overall_expected_quantity) as requested_qty, 
			sum(co.total_quantity) as ordered_qty,
			sum(co.total_payable_amount) as ordered_amount,
			sum(cp.paid_amount) as paid_amount
		from `tabSite` as s
			left join `tabCustomer` c on c.customer_id = s.user 
			left join `tabSite Item` si on si.parent = s.name and si.item_sub_group = '{item_sub_group}'
			left join `tabCustomer Order` co on co.site = s.name and co.docstatus = 1
			left join `tabCustomer Payment` cp on cp.site = s.name and co.docstatus = 1
		where s.creation between '{from_date}' and '{to_date}'
		{cond}
		group by site, site_date, site_type, construction_type
		order by s.creation
	""".format(
		item_sub_group=filters.item_sub_group,
		from_date = filters.from_date, 
		to_date = filters.to_date,
		cond = cond), as_dict=True)
	return data

def get_conditions(filters):
	cond = ""
	if filters.dzongkhag:
		cond += """ and s.dzongkhag = "{}" """.format(filters.dzongkhag)
	#if not filters.cost_center:
	#	return " and so.docstatus = 10"
	return cond

def get_columns(filters):
	columns = [
		{
		  	"fieldname": "site",
		  	"label": "Site#",
		  	"fieldtype": "Link",
		  	"options": "Site",
		  	"width": 100
		},
		{
		  	"fieldname": "site_type",
		  	"label": "Site Type",
		  	"fieldtype": "Link",
		  	"options": "Site Type",
		  	"width": 100
		},
		{
		  	"fieldname": "construction_type",
		  	"label": "Construction Type",
		  	"fieldtype": "Link",
		  	"options": "Construction Type",
		  	"width": 100
		},
		{
		  	"fieldname": "site_date",
		  	"label": "Reg. Date",
		  	"fieldtype": "Date",
		  	"width": 100
		},
		{
		  	"fieldname": "approval_no",
		  	"label": "Construction Approval No",
		  	"fieldtype": "Data",
		},
		{
		  	"fieldname": "customer",
		  	"label": "Customer",
		  	"fieldtype": "Link",
			"options": "Customer",
		  	"width": 150
		},
		{
		  	"fieldname": "dzongkhag",
		  	"label": "Dzongkhag",
		  	"fieldtype": "Link",
			"options": "Dzongkhags"
		},
		{
		  	"fieldname": "requested_qty",
		  	"label": "Overall Req. Qty",
		  	"fieldtype": "Float",
		  	"width": 120
		},
		{
		  	"fieldname": "ordered_qty",
		  	"label": "Ordered Qty",
		  	"fieldtype": "Float",
		  	"width": 120
		},
		{
		  	"fieldname": "ordered_amount",
		  	"label": "Total Order Amount",
		  	"fieldtype": "Currency",
		  	"width": 120
		},
		{
		  	"fieldname": "ordered_amount",
		  	"label": "Total Paid Amount",
		  	"fieldtype": "Currency",
		  	"width": 120
		},
	]

	return columns
