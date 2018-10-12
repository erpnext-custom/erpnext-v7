# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers, get_period_date
from frappe.utils import flt
from erpnext.custom_utils import get_production_groups

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_data(filters):
	data = []
	conditions = get_conditions(filters)

	group_by = get_group_by(filters)
	order_by = get_order_by(filters)
	total_qty = '1'
	if filters.show_aggregate:
		total_qty = "sum(qty) as total_qty"

	query = "select pe.posting_date, pe.item_code, pe.item_name, pe.item_group, pe.item_sub_group, pe.qty, pe.uom, pe.branch, pe.location, pe.adhoc_production, pe.company, pe.warehouse, pe.timber_class, pe.timber_type, pe.timber_species, cc.parent_cost_center as region, {0} from `tabProduction Entry` pe, `tabCost Center` cc where cc.name = pe.cost_center {1} {2} {3}".format(total_qty, conditions, group_by, order_by)
	abbr = " - " + str(frappe.db.get_value("Company", filters.company, "abbr"))

	total_qty = 0
	for a in frappe.db.sql(query, as_dict=1):
		a.region = str(a.region).replace(abbr, "")
		if filters.show_aggregate:
			a.qty = a.total_qty
		total_qty += flt(a.qty)
		data.append(a)
	data.append({"qty": total_qty, "region": frappe.bold("TOTAL")})

	return data

def get_group_by(filters):
	if filters.show_aggregate:
		group_by = " group by branch, location, item_sub_group"
	else:
		group_by = ""

	return group_by

def get_order_by(filters):
	return " order by region, location, item_group, item_sub_group"

def get_conditions(filters):
	if not filters.cost_center:
		return " and pe.docstatus = 10"

	all_ccs = get_child_cost_centers(filters.cost_center)
	if not all_ccs:
		return " and pe.docstatus = 10"

	all_branch = [str("DUMMY")]
	for a in all_ccs:
		branch = frappe.db.sql("select name from tabBranch where cost_center = %s", a, as_dict=1)
		if branch:
			all_branch.append(str(branch[0].name))

	condition = " and pe.branch in {0} ".format(tuple(all_branch))

	if filters.location:
		condition += " and pe.location = '{0}'".format(filters.location)

	filters.from_date, filters.to_date = get_period_date(filters.fiscal_year, filters.report_period)
	condition += " and posting_date between '{0}' and '{1}'".format(filters.from_date, filters.from_date)

	return condition

def get_columns(filters):
	columns = [
		{
			"fieldname": "region",
			"label": "Region",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "branch",
			"label": "Branch",
			"fieldtype": "Link",
			"options": "Branch",
			"width": 120
		},
		{
			"fieldname": "location",
			"label": "Location",
			"fieldtype": "Link",
			"options": "Location",
			"width": 120
		},
		{
			"fieldname": "item_group",
			"label": "Group",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "item_sub_group",
			"label": "Sub Group",
			"fieldtype": "Link",
			"options": "Item Sub Group",
			"width": 120
		},
		{
			"fieldname": "qty",
			"label": "Quantity",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "uom",
			"label": "UOM",
			"fieldtype": "Link",
			"options": "UoM",
			"width": 100
		},
	]

	if not filters.show_aggregate:
		columns.insert(3, {
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": 100
		})
	
		columns.insert(6, {
			"fieldname": "item_code",
			"label": "Material Code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		})
	
		columns.insert(9, {
			"fieldname": "timber_class",
			"label": "Class",
			"fieldtype": "Link",
			"options": "Timber Class",
			"width": 100
		})
		columns.insert(10, {
			"fieldname": "timber_species",
			"label": "Species",
			"fieldtype": "Link",
			"options": "Timber Species",
			"width": 100
		})
		columns.insert(11, {
			"fieldname": "timber_type",
			"label": "Type",
			"fieldtype": "Data",
			"width": 100
		})

	return columns

