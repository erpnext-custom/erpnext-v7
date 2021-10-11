# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
		data = []
		columns, data_set = get_columns(filters), get_data(filters)
		for a in data_set:
			if filters.summary:
				if filters.report_by == "Sales Order":
					data.append([a.name, a.branch, a.customer, a.customer_group, a.transaction_date, a.item_sub_group, a.qty, a.delivered_qty, a.stock_uom, a.amount, a.discount_or_cost_amount, a.additional_cost, a.net_amount])
				elif filters.report_by == "Sales Invoice":
					data.append([a.name, a.branch, a.customer, a.customer_group, a.posting_date, a.item_sub_group, a.business_activity, a.qty, a.delivered_qty, a.stock_uom, a.amount, a.discount_or_cost_amount, a.additional_cost, a.net_amount])
				else:
					data.append([a.name, a.branch, a.customer, a.customer_group, a.posting_date, a.item_sub_group, a.qty, a.total, a.discount_or_cost_amount, a.additional_cost, a.net_amount, a.vehicle, a.drivers_name, a.contact_no, a.transportation_rate, a.total_distance, a.transportation_charges])
			else:
				if filters.report_by == "Sales Order":
					data.append([a.name, a.branch, a.customer, a.customer_group, a.transaction_date, a.item_code, a.item_name, a.item_sub_group, a.qty, a.delivered_qty, a.stock_uom, a.rate, a.amount])
				elif filters.report_by == "Sales Invoice":
					data.append([a.name, a.branch, a.customer, a.customer_group, a.transaction_date, a.item_code, a.item_name, a.item_sub_group, a.business_activity, a.qty, a.delivered_qty, a.stock_uom, a.rate, a.amount])
				else:
					data.append([a.name, a.against_sales_order, a.business_activity, a.branch, a.customer, a.customer_group, a.posting_date, a.item_code, a.item_name, a.item_sub_group, a.qty, a.rate, a.amount, a.vehicle, a.drivers_name, a.contact_no, a.transportation_rate, a.total_distance, a.transportation_charges])

		return columns, data


def get_columns(filters=None):
	if filters.summary:
		if filters.report_by == "Sales Order":
			columns = [
				  _("Sales Order") + ":Link/Sales Order:100",
				  _("Branch") + ":Link/Branch:120",
				  _("Customer") + ":Link/Customer:150",
				  _("Customer Group") + ":Data:200", 
				  _("Posting Date") + ":Date:100",
				  _("Sub Group") + ":Data:100",
				  _("Actual Qty") + ":Float:90",
				  _("Qty Delivered") + ":Float:90",
				  _("UOM") + ":Data:90",
				  _("Amount") + ":Currency:100",
				  _("Discount") + ":Currency:120",
				  _("Additional Cost") + ":Currency:120",
				  _("Net Total")+":Currency:120"
			]
		elif filters.report_by == "Sales Invoice":
			columns = [
				  _("Sales Invoice") + ":Link/Sales Invoice:100",
				  _("Branch") + ":Link/Branch:120",
				  _("Customer") + ":Link/Customer:150",
				  _("Customer Group") + ":Data:200", 
				  _("Posting Date") + ":Date:100",
				  _("Sub Group") + ":Data:100",
				  _("Business Activity") + ":Data:100",
				  _("Billed Qty") + ":Float:90",
				  _("Qty Delivered") + ":Float:90",
				  _("UOM") + ":Data:90",
				  _("Amount") + ":Currency:100",
				  _("Discount") + ":Currency:120",
				  _("Additional Cost") + ":Currency:120",
				  _("Net Total")+":Currency:120"
			]
		else:
			columns = [
				  _("Delivery Note") + ":Link/Delivery Note:100", 
				#   _("Sales Order") + ":Link/Sales Order:100",
				  _("Branch") + ":Link/Branch:120",
				  _("Customer") + ":Link/Customer:150", 
				  _("Customer Group") + ":Data:200", 
				  _("Posting Date") + ":Date:100",
				  _("Sub Group") + ":Data:100", 
				  _("Qty Delivered") + ":Float:90",
				  _("Amount") + ":Currency:100",
				  _("Discount") + ":Currency:120",
				  _("Additional Cost") + ":Currency:120",
				  _("Net Total")+":Currency:120",
				  _("Vehicle") + ":Link/Vehicle:120", 
				  _("Driver") + ":Data:120", 
				  _("Contact No") + ":Data:120",
				  _("Transporation Rate") + ":Float:100", 
				  _("Distance") + ":Float:100", 
				  _("Transportation Charges") + ":Currency:100"
			]
	else:
		if filters.report_by == "Sales Order":
			columns = [
				  _("Sales Order") + ":Link/Sales Order:100",
				  _("Branch") + ":Link/Branch:180",
				  _("Customer") + ":Link/Customer:150", 
				  _("Customer Group") + ":Data:200", 
				  _("Posting Date") + ":Date:100", 
				  _("Item Code") + ":Link/Item: 80", 
				  _("Item Name") + ":Data:150", 
				  _("Sub Group") + ":Data:100",
				  _("Actual Qty")+ ":Float:100",
				  _("Qty Delivered") + ":Float:90",
				  _("UOM") + ":Data:90",
				  _("Rate") + ":Currency:90", 
				  _("Amount") + ":Currency:100"
				]
		if filters.report_by == "Sales Invoice":
			columns = [
				  _("Sales Invoice") + ":Link/Sales Invoice:100",
				  _("Branch") + ":Link/Branch:180",
				  _("Customer") + ":Link/Customer:150", 
				  _("Customer Group") + ":Data:200", 
				  _("Posting Date") + ":Date:100", 
				  _("Item Code") + ":Link/Item: 80", 
				  _("Item Name") + ":Data:150", 
				  _("Sub Group") + ":Data:100",
				  _("Business Activity") + ":Data:100",
				  _("Billed Qty")+ ":Float:100",
				  _("Qty Delivered") + ":Float:90",
				  _("UOM") + ":Data:90",
				  _("Rate") + ":Currency:90", 
				  _("Amount") + ":Currency:100"
				]
		else:
			columns = [
				  _("Delivery Note") + ":Link/Delivery Note:100", 
				  _("Sales Order") + ":Link/Sales Order:100",
				  _("Business Activity") + ":Link/Business Activity:100",
				  _("Branch") + ":Link/Branch:120",
				  _("Customer") + ":Link/Customer:150", 
				  _("Customer Group") + ":Data:200", 
				  _("Posting Date") + ":Date:100", 
				  _("Item Code") + ":Link/Item: 80", 
				  _("Item Name") + ":Data:150", 
				  _("Sub Group") + ":Data:100", 
				  _("Qty Delivered") + ":Float:90", 
				  _("Rate") + ":Float:90", 
				  _("Amount") + ":Currency:100",
				  _("Vehicle") + ":Link/Vehicle:120", 
				  _("Driver") + ":Data:120", 
				  _("Contact No") + ":Data:120",
				  _("Transporation Rate") + ":Float:100", 
				  _("Distance") + ":Float:100", 
				  _("Transportation Charges") + ":Currency:100"
				]
        return columns

def get_data(filters=None):
	cond = get_conditions(filters)
	outer_cond = get_outer_cond(filters)
	data = []

	if filters.report_by == "Sales Order":
		if filters.summary:
			cols = "so.name, so.branch, so.customer, so.customer_group, so.transaction_date, i.item_sub_group, so.total_quantity as qty, sum(soi.delivered_qty) as delivered_qty, soi.stock_uom, so.total, so.discount_or_cost_amount, so.additional_cost, (so.total - so.discount_or_cost_amount + so.additional_cost) as net_amount"
			group_by = " group by so.name"
		else:
			cols = "so.name, so.branch, so.customer, so.customer_group, so.transaction_date, soi.item_code, soi.item_name, i.item_sub_group, soi.qty as qty, soi.delivered_qty, soi.stock_uom, soi.rate, soi.amount"
			group_by = "and 1 = 1"
   
		query = """
		select * from (
			select {0}
			from `tabSales Order` so 
			inner join `tabSales Order Item` soi on so.name = soi.parent
			inner join `tabItem` i on soi.item_code = i.name
			where so.docstatus = 1
			{1} {2} ) as data where 1 = 1 {3}
			""".format(cols, cond, group_by, outer_cond)

	elif filters.report_by == "Sales Invoice":
		if filters.summary:
			cols = "si.name, si.branch, si.customer, si.customer_group, si.posting_date, i.item_sub_group, sii.business_activity, sum(sii.qty) as qty, sum(sii.delivered_qty) as delivered_qty, sii.stock_uom, si.total, si.discount_or_cost_amount, si.additional_cost, (si.total - si.discount_or_cost_amount + si.additional_cost) as net_amount"
			group_by = " group by si.name"
		else:
			cols = "si.name, si.branch, si.customer, si.customer_group, si.posting_date, sii.item_code, sii.item_name, i.item_sub_group, sii.business_activity, sii.qty as qty, sii.delivered_qty, sii.stock_uom, sii.rate, sii.amount"
			group_by = " and 1 = 1"
   
   		query = """
		select * from (
			select {0}
			from `tabSales Invoice` si
			inner join `tabSales Invoice Item` sii on si.name = sii.parent
			inner join `tabItem` i on sii.item_code = i.name
			where si.docstatus = 1
			{1} {2} ) as data where 1 = 1 {3}
			""".format(cols, cond, group_by, outer_cond)
		# frappe.msgprint(query)
	else:
		if filters.summary:
			cols = "dn.name as name, dn.branch, dn.customer, dn.customer_group, dn.posting_date, i.item_sub_group, sum(dni.qty) as qty, dn.total, dn.discount_or_cost_amount, dn.additional_cost, (dn.total - dn.discount_or_cost_amount + dn.additional_cost) as net_amount, dn.vehicle, dn.drivers_name, dn.contact_no, dn.transportation_rate, dn.total_distance, dn.transportation_charges"
			group_by = " group by dn.name"
			group_by_outer = " group by data.name"

		else:
			cols = "dn.name, dni.against_sales_order, dni.business_activity, dn.branch, dn.customer, dn.customer_group, dn.posting_date, dni.item_code, dni.item_name, i.item_sub_group, dni.qty as qty, dni.rate, dni.amount, dn.vehicle, dn.drivers_name, dn.contact_no, dn.transportation_rate, dn.total_distance, dn.transportation_charges"
			group_by = " and 1 = 1"
			group_by_outer = " and 1 = 1"
		
		query = """
			select * from (
			select {0}
			from `tabDelivery Note` dn 
			inner join `tabDelivery Note Item` dni on dn.name = dni.parent
			inner join `tabItem` i on dni.item_code = i.name
			where dn.docstatus = 1
			{1} {2}) as data where 1 = 1 {3} {4}
			""".format(cols, cond, group_by, outer_cond, group_by_outer)

		
		

        #frappe.throw(str(query))
	data = frappe.db.sql(query, as_dict=1)
	#row = {}
        #for a in  frappe.db.sql(query, as_dict=True):
	#	row = {"":,""}
	# frappe.msgprint(str(data	))
	return data
def get_outer_cond(filters=None):
	outer_cond = ""
	if filters.get("volume"):
		outer_cond += " and data.qty = {0}".format(filters.get("volume"))
	return outer_cond
			
def get_conditions(filters=None):
        cond=""

        if filters.from_date and filters.to_date:
		if filters.report_by == "Sales Order":
			cond += " and so.transaction_date between '" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"
		elif filters.report_by == "Sales Invoice":
			cond += " and si.posting_date between '" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"
		else:
			cond += " and dn.posting_date between'" + str(filters.from_date) + "' and '" + str(filters.to_date) + "'"

        if filters.cost_center:
                all_ccs = get_child_cost_centers(filters.cost_center)
		if filters.report_by == "Sales Order":
			cond += " and so.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))
		if filters.report_by == "Sales Invoice":
			cond += " and si.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))
		else:
			cond += " and dn.branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))

	if filters.item_group:
		cond += " and i.item_group = '" + str(filters.item_group) + "'"
	#	cond += " and exists (select 1 from `tabItem` i where i.item_group = '"+ str(filters.item_group) +"' and i.item_code = soi.item_code)"
	
	if filters.customer:
		if filters.report_by == "Sales Order":
			cond += " and so.customer = '"+str(filters.customer)+"'"
		if filters.report_by == "Sales Invoice":
			cond += " and si.customer = '"+str(filters.customer)+"'"
		else:
			cond += " and dn.customer = '"+str(filters.customer)+"'"

	if filters.customer_group:
		if filters.report_by == "Sales Order":
			cond += " and so.customer_group = '"+str(filters.customer_group)+"'"
		if filters.report_by == "Sales Invoice":
			cond += " and si.customer_group = '"+str(filters.customer_group)+"'"
		else:
			cond += " and dn.customer_group = '"+str(filters.customer_group)+"'"

	if filters.item_sub_group:
		cond += " and i.item_sub_group = '" + str(filters.item_sub_group) + "'"
		# cond += " and exists(select 1 from `tabItem` i where i.item_sub_group = '"+ str(filters.item_sub_group)+"' and i.item_code = soi.item_code)"

	if filters.item:
		cond += " and i.item_code = '" + str(filters.item) + "'"
	

	if filters.warehouse:
		if filters.report_by == "Sales Order":
			cond += " and soi.warehouse = '" + str(filters.warehouse) + "'"
		if filters.report_by == "Sales Invoice":
			cond += " and sii.warehouse = '" + str(filters.warehouse) + "'"
		else:
			cond += " and dni.warehouse = '" + str(filters.warehouse) + "'"
	if filters.branch:
		branch = str(filters.branch)
		branch = branch.replace(' - NHDCL','')
		if filters.report_by == "Sales Order":
			cond += " and so.branch = '"+branch+"'"
		if filters.report_by == "Sales Invoice":
			cond += " and si.branch = '"+branch+"'"
		else:
			cond += " and dn.branch = '"+branch+"'"
	if filters.business_activity:
		if filters.report_by == "Sales Order":
			frappe.throw("Business Acitivity filter only applies for report based on Delivery Note and Sales Invoice")
		elif not filters.summary:
			if filters.report_by == "Delivery Note":
				cond += """ and dni.business_activity = "{0}" """.format(filters.business_activity)
			elif filters.report_by == "Sales Invoice":
				cond += """ and sii.business_activity = "{0}" """.format(filters.business_activity)
		elif filters.summary:
			if filters.report_by == "Sales Invoice":
				cond += """ and sii.business_activity = "{0}" """.format(filters.business_activity)


		else:
			frappe.throw("This filter is not applicable for summary.")

        return cond
