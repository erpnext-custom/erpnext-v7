# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange
from erpnext.accounts.utils import get_child_cost_centers


def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

def get_data(filters):
	query = """
		select * from 
		(
			select 
				case when ll.sales_order != 'NULL' then 'Sold' when ll.production != 'NULL' then 'Taken For Sawing' when ll.stock_entry != 'NULL' then 'Stock Transfered' else 'Unsold' end as status, 
				lld.timber_class as timber_class , ll.posting_date as posting_date, lld.item as item_code, lld.item_name, lld.item_sub_group as type, 
				lld.total_volume as volume, lld.total_pieces as pieces, ll.lot_no, monthname(ll.posting_date) as month,ll.branch,ll.warehouse 
			from `tabLot List` ll , `tabLot List Details` lld 
			where ll.name = lld.parent and ll.docstatus=1
		) as data 
		where 
			posting_date >= '{0}' and posting_date <= '{1}'
		""".format(filters.from_date, filters.to_date)

	if filters.cost_center:
		all_ccs = get_child_cost_centers(filters.cost_center)
		query += " and branch in (select name from `tabBranch` b where b.cost_center in {0} )".format(tuple(all_ccs))

	if filters.branch:
		branch = str(filters.branch)
		branch = branch.replace(' - NRDCL','')
		query += " and branch = '"+branch+"'"

	if filters.warehouse:
		query+=" and warehouse = \'"+filters.warehouse+"\'"

	if filters.item_group:
		query+=" and type in (select distinct i.item_sub_group from `tabItem` i where i.item_group = \'"+filters.item_group+"\')"

	if filters.item_code:
		query+=" and item = \'"+filters.item_code+"\'"
	
	if filters.status:
		query+=" and status = \'"+filters.status+"\'"
	
	if filters.timber_class:
		query+=" and timber_class = \'"+filters.timber_class+"\'"

	data = frappe.db.sql(query, as_dict=True)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": _("Item Code"),
			"fieldtype": "Link",
			"options" : "Item",
			"width": 120
		},
		{
			"fieldname": "item_name",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "type",
			"label": _("Type"),
			"fieldtype": "Data",
			"width": 130
		},
			{
			"fieldname": "timber_class",
			"label": _("Timber Class"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "lot_no",
			"label": _("Lot Number"),
			"fieldtype": "Link",
			"options":"Lot List",
			"width": 120
		},
		{
			"fieldname": "pieces",
			"label": _("Total Pieces"),
			"fieldtype": "Int",
			"width": 120
		},
		{
			"fieldname": "volume",
			"label": _("Total Volume"),
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "month",
			"label": _("Month"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "branch",
			"label": _("Branch"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Data",
			"width": 130
		}
	]
	
	return columns
