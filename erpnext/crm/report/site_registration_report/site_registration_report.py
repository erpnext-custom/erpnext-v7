# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt
import frappe
from frappe import _
import collections

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	data = []

	sites    = get_site_details(filters)
	orders   = get_order_details(filters)
	payments = get_payment_details(filters)

	sites    = collections.OrderedDict(sorted(sites.items()))
	for site, row in sites.iteritems():
		if orders.get(site):
			row.update(orders.get(site))
		if payments.get(site):
			row.update(payments.get(site))

		data.append(row)

	return data

def get_payment_details(filters):
	data = frappe._dict()

	payments = frappe.db.sql("""
		select cp.site,
			sum(cp.paid_amount) paid_amount
		from `tabCustomer Payment` cp
		where exists(
			select 1
			from `tabSite` as s
			where s.name = cp.site 
			and s.creation between '{from_date}' and '{to_date}'
		)
		and cp.docstatus = 1
		group by cp.site
	""".format(
                from_date = filters.from_date,
                to_date = filters.to_date), as_dict=True)
	for i in payments:
		data.setdefault(i.site,i)

	return data

def get_order_details(filters):
	data = frappe._dict()

	orders = frappe.db.sql("""
		select co.site,
			sum(co.total_quantity) ordered_quantity,
			sum(co.total_payable_amount) ordered_amount
		from `tabCustomer Order` co
		where exists(
			select 1
			from `tabSite` as s
			where s.name = co.site 
			and s.creation between '{from_date}' and '{to_date}'
		)
		and co.docstatus = 1
		group by co.site
	""".format(
                from_date = filters.from_date,
                to_date = filters.to_date), as_dict=True)
	for i in orders:
		data.setdefault(i.site,i)
	return data

def get_site_details(filters):
	data = frappe._dict()

	cond = get_conditions(filters)
	sites= frappe.db.sql("""
		select s.name site, date(s.creation) as site_date, s.site_type, s.construction_type, 
			s.approval_no, c.name as customer, c.customer_group, s.dzongkhag,
			sum(si.overall_expected_quantity) as requested_quantity 
		from `tabSite` as s
			left join `tabCustomer` c on c.customer_id = s.user 
			left join `tabSite Item` si on si.parent = s.name and si.item_sub_group = '{item_sub_group}'
		where s.creation between '{from_date}' and '{to_date}'
		{cond}
		group by s.name, site_date, s.site_type, s.construction_type, s.approval_no,
			c.name, s.dzongkhag
	""".format(
		item_sub_group=filters.item_sub_group,
		from_date = filters.from_date, 
		to_date = filters.to_date,
		cond = cond), as_dict=True)
	for i in sites:
		data.setdefault(i.site,i)

	return data

def get_conditions(filters):
	cond = ""
	if filters.dzongkhag:
		cond += """ and s.dzongkhag = "{}" """.format(filters.dzongkhag)

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
		  	"width": 120
		},
		{
		  	"fieldname": "customer",
		  	"label": "Customer",
		  	"fieldtype": "Link",
			"options": "Customer",
		  	"width": 150
		},
		{
		  	"fieldname": "customer_group",
		  	"label": "Customer Group",
		  	"fieldtype": "Link",
			"options": "Customer Group",
		},
		{
		  	"fieldname": "dzongkhag",
		  	"label": "Dzongkhag",
		  	"fieldtype": "Link",
			"options": "Dzongkhags"
		},
		{
		  	"fieldname": "requested_quantity",
		  	"label": "Overall Req. Qty",
		  	"fieldtype": "Float",
		  	"width": 120
		},
		{
		  	"fieldname": "ordered_quantity",
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
		  	"fieldname": "paid_amount",
		  	"label": "Total Paid Amount",
		  	"fieldtype": "Currency",
		  	"width": 120
		},
	]

	return columns
