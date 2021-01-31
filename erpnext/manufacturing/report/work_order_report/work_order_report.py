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
            _("Item Code") + ":Link/Item:100",
            _("Item Name") + ":Data:170",
			_("Item Sub Group type") + ":Link/Item Sub Group Type:150",
            _("Total") + ":Data:120",
            _("In Progress") + ":Data:120",
            _("Completed") + ":Data:90"
	]
	return columns

def get_progress_data(filters):
	query = """select 
					wo.creation
					, wo.name
					, wo.production_item
					, wo.item_name
					,i.item_sub_group_type
					, wo.qty
					, (wo.qty-wo.produced_qty) as progress
					, wo.produced_qty
         from `tabWork Order` wo, `tabItem` i
		 where wo.docstatus =1 and wo.status ='In Process' and wo.qty != wo.produced_qty and i.name=wo.production_item
		  """
		#wo.status != 'Stopped'
	if filters.get("from_date") and filters.get("to_date"):
		query += " and wo.creation between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	return frappe.db.sql(query)

def get_completed_columns(filters=None):
	columns=[
		_("Work Order") + ":Link/Work Order:200",
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
	data = frappe.db.sql("""
		select 
			wo.name
			, wo.creation
			, wo.production_item
			, wo.item_name
			, i.item_sub_group_type
			, wo.qty
			, wo.produced_qty
			, bom.total_cost
			, wo.job_no
		from `tabWork Order` wo
			left join `tabBOM` as bom on bom.name = wo.bom_no
			join `tabItem` i on i.name=wo.production_item
		where wo.docstatus = 1 and wo.status='Completed' and wo.produced_qty=wo.qty 	
		
	""")
	return data
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
