# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
        columns, data = get_columns(filters), get_data(filters)
        return columns, data


def get_columns(filters=None):
	if filters.aggregate:
		if filters.report_by == "Sales Order":
			columns = [
				_("Branch") + ":Link/Sales Order:150", _("Location") + ":Data/120", _("Customer") + ":Link/Customer:150", _("Customer Name") + ":Data:200", _("Customer Group") + ":Data:200", _("Sub Item Group") + ":Data:150", _("Sales Qty") + ":Float:120",_("Delivered Qty") + ":Float:120", _("Amount") + ":Currency:120"
			]

		else:
			columns = [
                                _("Branch") + ":Link/Sales Order:150", _("Location") + ":Data/120", _("Customer") + ":Link/Customer:150", _("Customer Name") + ":Data:200", _("Customer Group") + ":Data:200", _("Sub Item Group") + ":Data:150", _("Delivered Qty") + ":Float:120", _("Amount") + ":Currency:120"
                        ]
	else:
		if filters.report_by == "Sales Order":
			columns = [
				  _("Sales Order") + ":Link/Sales Order:100", _("Branch") + ":Link/Branch:120", _("Customer") + ":Link/Customer:150", _("Customer Name") + ":Data:200", _("Customer Group") + ":Data:200", _("Posting Date") + ":Date:100", 
				  _("Item Code") + ":Link/Item: 80", _("Item Name") + ":Data:150", _("Sub Group") + ":Data:100",
				  _("Customer") + ":Link/Customer:140", _("Actual Qty") + ":Float:90", _("Qty Delivered") + ":Float:90",
				  _("Rate") + ":Float:90", _("Amount") + ":Currency:100"
				]
		else:
			columns = [
				  _("Delivery Note") + ":Link/Delivery Note:100", _("Sales Order") + ":Link/Sales Order:100", _("Branch") + ":Link/Branch:120",
				   _("Customer") + ":Link/Customer:150", _("Customer Name") + ":Data:200", _("Customer Group") + ":Data:200", 
				  _("Posting Date") + ":Date:100", _("Item Code") + ":Link/Item: 80", _("Item Name") + ":Data:150", _("Sub Group") + ":Data:100",
				  _("Customer") + ":Link/Customer:140", _("Qty Delivered") + ":Float:90", _("Rate") + ":Float:90", _("Amount") + ":Currency:100",
				  _("Vehicle") + ":Link/Vehicle:120", _("Driver") + ":Data:120", _("Contact No") + ":Data:120",
				  _("Transporation Rate") + ":Float:100", _("Distance") + ":Float:100", _("Transportation Charges") + ":Currency:100"
				]
        return columns

def get_data(filters=None):
        cond = get_conditions(filters)
        data = []
	
	if filters.report_by == "Sales Order":
		if filters.aggregate:
			cols = "so.branch, so.location, so.customer, so.customer_name, so.customer_group, i.item_sub_group, sum(soi.qty) as qty, sum(soi.delivered_qty), sum(soi.amount)"
			group_by = "group by so.branch, i.item_sub_group"
		else:
			cols = "so.name, so.branch, so.customer, so.customer_name, so.customer_group, so.transaction_date, soi.item_code, soi.item_name, i.item_sub_group, so.customer, soi.qty as qty, soi.delivered_qty, soi.rate, soi.amount"
			group_by = "and 1 = 1"
		
		
		query = """
			select {0}
			from `tabSales Order` so 
			inner join `tabSales Order Item` soi on so.name = soi.parent 
			inner join `tabItem` i on soi.item_code = i.name
			where so.docstatus = 1
			{1} {2}
			""".format(cols, cond, group_by)

	else:
		if filters.aggregate:
			cols = "dn.branch, dn.customer, dn.customer_name, dn.customer_group, dni.location, i.item_sub_group, sum(dni.qty) as qty, sum(dni.amount)"
			group_by = "group by dn.branch, i.item_sub_group"
		else:
			cols = "dn.name, dni.against_sales_order, dn.branch, dn.customer, dn.customer_name, dn.customer_group, dn.posting_date, dni.item_code, dni.item_name, i.item_sub_group, dn.customer, dni.qty as qty, dni.rate, dni.amount, dn.vehicle, dn.drivers_name, dn.contact_no, dn.transportation_rate, dn.total_distance, dn.transportation_charges"
			group_by = " and 1 = 1"
		
		query = """
			select {0}
			from `tabDelivery Note` dn 
			inner join `tabDelivery Note Item` dni on dn.name = dni.parent
			inner join `tabItem` i on dni.item_code = i.name
			where dn.docstatus = 1
			{1} {2}
			""".format(cols, cond, group_by)

		
		

        #frappe.throw(str(query))
	data = frappe.db.sql(query)
	#row = {}
        #for a in  frappe.db.sql(query, as_dict=True):
	#	row = {"":,""}
        return data


def get_conditions(filters=None):
        cond=""

        if filters.from_date and filters.to_date:
		if filters.report_by == "Sales Order":
                	cond += " and so.transaction_date between '" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"
		else:
			cond += " and dn.posting_date between'" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"

        if filters.cost_center:
                all_ccs = get_child_cost_centers(filters.cost_center)
		if filters.report_by == "Sales Order":
			cond += " and so.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))
		else:
			cond += " and dn.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))

	if filters.item_group:
		cond += " and i.item_group = '" + str(filters.item_group) + "'"
	#	cond += " and exists (select 1 from `tabItem` i where i.item_group = '"+ str(filters.item_group) +"' and i.item_code = soi.item_code)"
	
	if filters.customer:
		if filters.report_by == "Sales Order":
			cond += " and so.customer = '"+str(filters.customer)+"'"
		else:
			cond += " and dn.customer = '"+str(filters.customer)+"'"

	if filters.customer_group:
		if filters.report_by == "Sales Order":
			cond += " and so.customer_group = '"+str(filters.customer_group)+"'"
		else:
			cond += " and dn.customer_group = '"+str(filters.customer_group)+"'"

	if filters.item_sub_group:
		cond += " and i.item_sub_group = '" + str(filters.item_sub_group) + "'"

	if filters.item:
		cond += " and i.item_code = '" + str(filters.item) + "'"
	

	if filters.warehouse:
		if filters.report_by == "Sales Order":
			cond += " and soi.warehouse = '" + str(filters.warehouse) + "'"
		else:
			cond += " and dni.warehouse = '" + str(filters.warehouse) + "'"
	if filters.branch:
		branch = str(filters.branch)
		branch = branch.replace(' - WCCL','')
		if filters.report_by == "Sales Order":
			cond += " and so.branch = '"+branch+"'"
		else:
			cond += " and dn.branch = '"+branch+"'"
	if filters.location and filters.report_by == "Delivery Note":
		cond += " and dni.location = '" + str(filters.location) + "'"	

        return cond
