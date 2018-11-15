# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data



def get_columns():
	columns = [
		_("Employee") + ":Link/Employee:120",
		_("Employee Name") + ":Data:150",
		_("Hiring Date") + ":Date:120",
		_("Equipment") + ":Link/Equipment:120",
		_("Equipment No") + ":Data:100",
		_("Hiring Hours") + ":Float:100",
		_("Cost Center") + ":Link/Cost Center:120",
	]

	return columns
def get_data(filters):

	conditions = []
	
	if filters.get("from_date") and filters.get("to_date"):
		conditions.append("d.hiring_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) +"\'")

	if filters.get("cost_center"):
		conditions.append("o.cost_center = \'" + str(filters.cost_center) + "\'")
	if filters.get("operator"):
		conditions.append("o.operator = \'" + str(filters.operator) +"\'")
	records = frappe.db.sql("""
			select o.operator, o.operator_name, d.hiring_date, d.equipment, d.equipment_no, d.total_hours, o.cost_center
			from `tabOperators Over Time Details` o inner join `tabOperator Hiring Details` d
			on o.name = d.parent
			where {conditions}
			order by d.hiring_date
			""".format(conditions = " and ". join(conditions)))
			
	return records


@frappe.whitelist()
def get_operators():
	options = []
	for d in frappe.db.sql("select distinct(operator) as operator, operator_name as operator_name from `tabOperators Over Time Details` ORDER BY operator_name", as_dict=True):
		options.append([d['operator'],d['operator_name']])
	return options		

	
