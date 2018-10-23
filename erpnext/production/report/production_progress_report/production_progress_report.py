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
	cc_condition = get_cc_conditions(filters)
	conditions = get_filter_conditions(filters)

	group_by = get_group_by(filters)
	order_by = get_order_by(filters)
	abbr = " - " + str(frappe.db.get_value("Company", filters.company, "abbr"))

	query = "select pe.cost_center, pe.branch, pe.location, cc.parent_cost_center as region, sum(qty) as total_qty from `tabProduction Entry` pe, `tabCost Center` cc where cc.name = pe.cost_center {0} {1} {2} {3}".format(cc_condition, conditions, group_by, order_by)

	for a in frappe.db.sql(query, as_dict=1):
		a.region = str(a.region).replace(abbr, "")
		target = get_target()
		if filters.branch:
			row = [a.region, a.branch, a.location, target]
			cond = " and location = '{0}'".format(a.location)
		else:
			row = [a.region, a.branch, target]
			cond = " and cost_center = '{0}'".format(a.cost_center)
		for b in get_production_groups(filters.production_group):
			qty = frappe.db.sql("select sum(pe.qty) from `tabProduction Entry` pe where 1 = 1 {0} and pe.item_sub_group = '{1}' {2}".format(conditions, str(b), cond))
			qty = qty and qty[0][0] or 0
			row.append(qty)
		data.append(row)

	return data

def get_target():
	return 0

def get_group_by(filters):
	if filters.branch:
		group_by = " group by region, branch, location"
	else:
		group_by = " group by region, branch"

	return group_by

def get_order_by(filters):
	return " order by region, location"

def get_cc_conditions(filters):
	if not filters.cost_center:
		return " and pe.docstatus = 10"

	all_ccs = get_child_cost_centers(filters.cost_center)
	condition = " and pe.cost_center in {0} ".format(tuple(all_ccs))	

	return condition

def get_filter_conditions(filters):
	condition = ""
	if filters.location:
		condition += " and pe.location = '{0}'".format(filters.location)

	filters.from_date, filters.to_date = get_period_date(filters.fiscal_year, filters.report_period)
	condition += " and pe.posting_date between '{0}' and '{1}'".format(filters.from_date, filters.to_date)

	return condition

def get_columns(filters):
	if filters.branch:
		columns = ["Region:Data:150", "Branch:Link/Branch:150", "Location:Link/Location:150", "Target Qty:Float:120"]
	else:
		columns = ["Region:Data:150", "Branch:Link/Branch:150", "Target Qty:Float:120"]

	for a in get_production_groups(filters.production_group):
		columns.append(str(str(a) + ":Float:100"))
	
	return columns

