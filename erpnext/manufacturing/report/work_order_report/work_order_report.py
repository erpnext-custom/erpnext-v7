# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

###############Created by Cheten Tshering on 14/09/2020 #######################
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters):
	if filters.get("report_type") == "In_Progress":
		columns = get_progress_columns(filters)
		data = get_progress_data(filters)
	else:
		columns = get_completed_columns(filters)
		data = get_completed_data(filters)
	return columns, data

def get_progress_columns(filters=None):
	columns = [
		 	_("Date ") + ":Date:120",
            _("Work Order.") + ":Link/Work Order:120",
            _("Item Code") + ":Link/Item:100",
            _("Item Name") + ":Data:170",
            _("Total") + ":Data:120",
            _("In Progress") + ":Data:120",
            _("Completed") + ":Data:90"
	]
	return columns

def get_progress_data(filters):
	query = """select creation, name,  production_item, item_name, qty, (qty-produced_qty) as progress, produced_qty
         from `tabWork Order` where docstatus =1 and status != 'Stopped' and qty != produced_qty """
	if filters.get("from_date") and filters.get("to_date"):
		query += " and creation between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	return frappe.db.sql(query)

def get_completed_columns(filters=None):
	columns=[
		_("Work Order") + ":Link/Work Order:200",
		_("Date") + ":Date:120",
		_("Item") + ":Link/Item:150",
		_("Item Name") + ":Link/Item:150",
		_("To Produce") + ":Int:100",
		_("Produced") + ":Int:100",
		_("COP") + ":Float:140"
	]
	return columns

def get_completed_data(filters=None):
	data = frappe.db.sql("""
		select wo.name, wo.creation, wo.production_item, wo.item_name, wo.qty, wo.produced_qty, bom.total_cost
		from `tabWork Order` wo
		left join `tabBOM` as bom on bom.name = wo.bom_no
		where wo.docstatus = 1 and wo.produced_qty=wo.qty
	""")
	return data