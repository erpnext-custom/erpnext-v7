# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

##########Created by Cheten Tshering on 14/09/2020 ###########################
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
            _("Branch") + ":Link/Branch:120",
            _("BOM No") + ":Link/BOM:120",
            _("Item Code") + ":Link/Item:100",
            _("Item Name") + ":Data:170",
			_("Item Sub Group type") + ":Link/Item Sub Group Type:150",
			_("Work in Progress Warehouse") + ":Link/Warehouse:150",
			_("Target Warehouse") + ":Link/Warehouse:150",
            _("Total") + ":Float:120",
            _("In Progress") + ":Float:120",
            _("Completed") + ":Float:90"
	]
	return columns

def get_progress_data(filters):
	query = """SELECT 
					wo.planned_start_date,
					wo.name,
					wo.branch,
					wo.bom_no,
					wo.production_item,
					wo.item_name,
					i.item_sub_group_type,
					wo.wip_warehouse,
					wo.fg_warehouse,
					wo.qty,
					(wo.qty-wo.produced_qty) as progress,
					wo.produced_qty
				FROM `tabWork Order` wo, `tabItem` i
				WHERE wo.docstatus =1 AND wo.status ='In Process' AND wo.qty != wo.produced_qty AND i.name=wo.production_item
		"""
		#wo.status != 'Stopped'
	if filters.get("from_date") and filters.get("to_date"):
		query += " AND wo.planned_start_date >= \'" + filters.from_date + "\' AND wo.planned_start_date <= \'"+ filters.to_date + "\'"
	if filters.get("cost_center"):
		if filters.get("branch"):
			query += " AND wo.branch = \'" + str(filters.branch).replace(' - NRDCL','') + "\'"
		else:
			query += " AND wo.branch in (select name from `tabBranch` where cost_center in (select name from `tabCost Center` where parent_cost_center = \'" + filters.cost_center + "\'))"
	if filters.get("item"):
		query += " AND wo.production_item = '{}'".format(filters.get("item"))

	
	return frappe.db.sql(query)

def get_completed_columns(filters=None):
	columns=[
		_("Work Order") + ":Link/Work Order:200",
        _("Branch") + ":Link/Branch:120",
		_("Date") + ":Date:120",
		_("Item") + ":Link/Item:150",
		_("Item Name") + ":Link/Item:150",
		_("Item Sub Group Type") + ":Link/Item Sub Group Type:150",
		_("To Produce") + ":Int:100",
		_("Produced") + ":Int:100",
		_("COP") + ":Float:140",
		_("Job_No") + "::80"
	]
	return columns

def get_completed_data(filters=None):
	query = """
		SELECT 
			wo.name,
			wo.branch,
			wo.planned_start_date,
			wo.production_item,
			i.item_name,
			i.item_sub_group_type,
			wo.qty,
			wo.produced_qty,
			bom.total_cost,
			wo.job_no
		FROM `tabWork Order` wo
			left join `tabBOM` as bom on bom.name = wo.bom_no
			join `tabItem` i on i.name=wo.production_item
		WHERE wo.docstatus = 1 AND wo.status='Completed' AND wo.produced_qty=wo.qty
			AND wo.planned_start_date >= '{0}' AND wo.planned_start_date <= '{1}'
	""".format(filters.from_date, filters.to_date)
	if filters.get("cost_center"):
		if filters.get("branch"):
			query += " AND wo.branch = \'" + str(filters.branch).replace(' - NRDCL','') + "\'"
		else:
			query += " AND wo.branch in (select name from `tabBranch` where cost_center in (select name from `tabCost Center` where parent_cost_center = \'" + filters.cost_center + "\'))"
	return frappe.db.sql(query)
# join `tabItem` i on i.name=wo.production_item
# 	SELECT
#   `tabWork Order`.name as "Work Order:Link/Work Order:200",
#   `tabWork Order`.creation as "Date:Date:120",
#   `tabWork Order`.production_item as "Item:Link/Item:150",
#   `tabWork Order`.item_name as "Item Name:Link/Item:150",
#   `tabWork Order`.qty as "To Produce:Int:100",
#   `tabWork Order`.produced_qty as "Produced:Int:100",
#    (select total_cost from `tabBOM` where name = `tabWork Order`.bom_no) as "COP:Float:140"
# FROM
#   `tabWork Order`
# WHERE
#   `tabWork Order`.docstatus=1
#   AND ifnull(`tabWork Order`.produced_qty,0) = `tabWork Order`.qty
