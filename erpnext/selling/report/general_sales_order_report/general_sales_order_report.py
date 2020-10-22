# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

#################Created by Cheten Tshering on 15/08/2020 ###########################
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_column(filters), get_data(filters)
	return columns, data

def get_column(filters=None):
	columns = [
		_("ID") + ":Link/Sales Order:100",
		_("Created By") + ":Data:150",
		_("Branch") + ":Link/Branch:150",
		_("Posting Date") + ":Data:100",
		_("Customer") + ":Link/Customer:150",
		_("Customer Group") + ":Link/Customer Group:150",
		_("Delivery Date") + ":Date:100",
		_("Grand Total") + ":Currency:100",
		_("Project") + ":Link/Project:150",
		_("Status") + ":Data:150",
		_("%Amount Billed") + ":Percent:150"
	]
	return columns

def get_data(filters=None):
	data = frappe.db.sql(
		'''
		SELECT 
			so.name,
			so.owner,
			so.branch,
			so.transaction_date,
			so.customer,
			so.customer_group,
			so.delivery_date,
			so.grand_total,
			so.project,
			so.status,
			so.per_billed
		FROM 
			`tabSales Order` as so
		WHERE so.docstatus = 1 and so.transaction_date between '{from_date}' and '{to_date}'
		'''.format(from_date = filters.from_date,
                to_date = filters.to_date))
	return data

		# {
		# 	"fieldname": "branch",
		# 	"label": _("Branch"),
		# 	"fieldtype": "Link",
		# 	"options":"Branch",
		# 	"width": 150
		# },
		# {
		# 	"fieldname": "transaction_date",
		# 	"label": _("Posting Date"),
		# 	"fieldtype": "Date",
		# 	"width": 150
		# },
		# {
		# 	"fieldname": "customer",
		# 	"label": _("Customer"),
		# 	"fieldtype": "Link",
		# 	"options":"Customer",
		# 	"width": 150
		# },
		# {
		# 	"fieldname": "customer_group",
		# 	"label": _("Customer Group"),
		# 	"fieldtype": "Link",
		# 	"options":"Customer Group",
		# 	"width": 150
		# },
		# {
		# 	"fieldname": "delivery_date",
		# 	"label": _("Delivery Date"),
		# 	"fieldtype": "Date",
		# 	"width": 100
		# },
		# {
		# 	"fieldname": "grand_total",
		# 	"label": _("Grand Total"),
		# 	"fieldtype": "Currency",
		# 	"width": 150
		# },
		# {
		# 	"fieldname": "project",
		# 	"label": _("Project"),
		# 	"fieldtype": "Link",
		# 	"options":"Project",
		# 	"width": 150
		# },
		# {
		# 	"fieldname": "branch",
		# 	"label": _("Branch"),
		# 	"fieldtype": "Link",
		# 	"options":"Branch",
		# 	"width": 150
		# },

