# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt

def execute(filters=None):
        columns = get_columns(filters)
        data = get_data(filters)
        return columns, data

def get_data(filters=None):
        data = []
	cond = get_conditions(filters)
	data = frappe.db.sql("""
		    select so.name, so.transaction_date, soi.item_code, soi.item_name, 
		    so.customer, soi.qty, soi.rate, soi.amount
		    from `tabSales Order` so, `tabSales Order Item` soi
		    where so.name = soi.parent
		    and so.docstatus = 1
		    {0}
		""".format(cond), as_dict=True)
	return data

def get_conditions(filters=None):
	if filters.from_date and filters.to_date:
		condition = " and so.transaction_date between '" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"
	if filters.cost_center:
		all_ccs = get_child_cost_centers(filters.cost_center)
		condition += " and so.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))

	return condition

def get_columns(filters=None):
	columns = [
		  _("Sales Order") + ":Link/Sales Order:100", _("Posting Date") + ":Date:100", _("Item Code") + ":Link/Item: 80", _("Item Name") + ":Data:150",
		  _("Customer") + ":Link/Customer:140", _("Qty") + ":Float:90", 
		  _("Rate") + ":Float:90", _("Amount") + ":Currency:100", 
	]

	return columns

