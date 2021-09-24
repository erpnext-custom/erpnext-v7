# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers

def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)
        return columns, data


def get_data(filters):
	query = """ select 
  so.name, so.customer,  so.customer_group, so.transaction_date, so.vehicle_nos, soi.item_code, soi.qty,
 soi.delivered_qty, (soi.qty - ifnull(soi.delivered_qty, 0)),  soi.base_rate, soi.base_amount,
 (soi.qty - ifnull(soi.delivered_qty, 0) *soi.base_rate) as total,
 b.actual_qty, b.projected_qty, so.delivery_date, soi.item_name, soi.description,soi.item_group, soi.warehouse
from `tabSales Order` so JOIN `tabSales Order Item` soi
 LEFT JOIN `tabBin` b ON (b.item_code = soi.item_code and b.warehouse = soi.warehouse)
where soi.parent = so.name and so.docstatus = 1 and so.status not in ("Stopped", "Closed") and ifnull(soi.delivered_qty,0) < ifnull(soi.qty,0)
 """
        # if filters.branch:
        #         query += " and so.branch = '{0}'".format(filters.branch)
    	if not filters.cost_center:
		return ""
	
	if not filters.branch:	
		all_ccs = get_child_cost_centers(filters.cost_center)
		query += " and so.branch in (select b.name from `tabCost Center` cc, `tabBranch` b where b.cost_center = cc.name and cc.name in {0})".format(tuple(all_ccs))
	else:
		branch = str(filters.get("branch"))
		branch = branch.replace(' - NRDCL','')
		query += " and so.branch = \'"+branch+"\'"
       
	# if filters.from_date and filters.to_date:
               
	# 	query += " and so.transaction_date between '{0}' and '{1}'".format(filters.get("from_date"), filters.get("to_date"))
      
        # frappe.msgprint(query)
        return frappe.db.sql(query)
        # frappe.msgprint(str(data))
    	# return query

def get_columns():
        return [

                ("Sales Order") + ":Link/Sales Order:190",
                ("Customer") + ":Link/Customer:120",
				("Customer Group")+":Link/Customer Group:200",
				("Date") + ":Date:120",
				("Vehicle No.") + ":Data:120",
                ("Material Code") + ":Data:120",
                ("QTY") + ":Float:100",
                ("Delivered QTY") + ":Float:120",
				 ("QTY to Deliver") + ":Float:120",
                ("Delivered Rate") + ":Float:120",
				("Delivered Amount") + ":Float:120",
				("Amount To Deliver") + ":Float:120",
				("Avaliable QTY") + ":Float:120",
				("Projected QTY") + ":Float:120",
				("Expected Delivery Date") + ":Date:120",
				("Material Name") + ":Data:120",
				("Description") + ":Data:120",
				("Material Group") +  ":Link/Item Group:200",
				("Warehouse") + ":Link/Warehouse:200"

        ] 
