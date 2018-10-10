# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from erpnext.accounts.utils import get_child_cost_centers
from frappe.utils import flt

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

	query = "select pe.item_code, pe.item_name, pe.item_group, pe.item_sub_group, pe.qty, pe.uom, pe.branch, pe.location, pe.adhoc_production, pe.company, pe.warehouse, pe.timber_class, pe.timber_type, pe.timber_species, cc.parent_cost_center as region, {0} from `tabProduction Entry` pe, `tabCost Center` cc where cc.name = pe.cost_center {1} {2} {3}".format(total_qty, conditions, group_by, order_by)
	abbr = " - " + str(frappe.db.get_value("Company", filters.company, "abbr"))

	for a in frappe.db.sql(query, as_dict=1):
		a.region = str(a.region).replace(abbr, "")
		if filters.show_aggregate:
			a.qty = a.total_qty
		a.qty = flt(a.qty)
		data.append(a)

	return data

def get_group_by(filters):
	if filters.show_aggregate:
		group_by = " group by branch, location, item_sub_group"
	else:
		group_by = ""

	if filters.item_group == "Minerial Products":
		cols = ""
	elif filters.item_group == "Timber Products":
		pass
	else:
		pass

	return group_by

def get_order_by(filters):
	return " order by region"

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

	if filters.production_type != "All":
		condition += " and pe.production_type = '{0}'".format(filters.production_type)

	if filters.location:
		condition += " and pe.location = '{0}'".format(filters.location)

	if filters.adhoc_production:
		condition += " and pe.adhoc_production = '{0}'".format(filters.adhoc_production)

	if filters.item_group:
		condition += " and pe.item_group = '{0}'".format(filters.item_group)

	if filters.item_sub_group:
		condition += " and pe.item_sub_group = '{0}'".format(filters.item_sub_group)

	if filters.item:
		condition += " and pe.item_code = '{0}'".format(filters.item)

	if filters.from_date and filters.to_date:
		condition += " and pe.posting_date between '{0}' and '{1}'".format(filters.from_date, filters.to_date)

	if filters.timber_species:
		condition += " and pe.timber_species = '{0}'".format(filters.timber_species)

	if filters.timber_class:
		condition += " and pe.timber_class = '{0}'".format(filters.timber_class)

	if filters.warehouse:
		condition += " and pe.warehouse = '{0}'".format(filters.warehouse)

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
			"fieldname": "item_sub_group",
			"label": "Sub Group",
			"fieldtype": "Link",
			"options": "Item Sub Group",
			"width": 100
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

	if filters.item_group == "Timber Products":
		columns.insert(4, {
			"fieldname": "timber_class",
			"label": "Class",
			"fieldtype": "Link",
			"options": "Timber Class",
			"width": 100
		})
		columns.insert(5, {
			"fieldname": "timber_species",
			"label": "Species",
			"fieldtype": "Link",
			"options": "Timber Species",
			"width": 100
		})
		columns.insert(6, {
			"fieldname": "timber_type",
			"label": "Type",
			"fieldtype": "Data",
			"width": 100
		})
	
	return columns

