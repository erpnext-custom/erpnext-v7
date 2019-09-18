# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def validate_filters(filters):
	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date cannot be greater than To Date"))

def get_data(filters):

	query = "select a.employee_name as employee,c.employee_group as designation,c.employee_subgroup as grade,sum(b.number_of_hours) as hours,sum(round(b.number_of_hours*a.rate,2)) as amount,c.cost_center from `tabOvertime Application Item` as b,`tabOvertime Application` as a join `tabEmployee` as c on a.employee_name=c.employee_name where b.parent=a.name and b.docstatus=1 and b.date>= \'"+str(filters.from_date)+"\' and b.date<=\'"+str(filters.to_date)+"\' group by a.employee_name order by a.employee_name asc"

	data = frappe.db.sql(query, as_dict=True)
	
	return data

def get_columns():
	return [
		{
			"fieldname": "employee",
			"label": _("Employee Name"),
			"fieldtype": "Link",
			"options": "Employee",
			"width": 120
		},
		{
			"fieldname": "designation",
			"label": _("Designation"),
			"fieldtype": "Link",
			"options": "Designation",
			"width": 130
		},
		{
			"fieldname": "grade",
			"label": _("Grade"),
			"fieldtype": "Link",
			"options": "Employee Grade",
			"width": 120
		},
		{
			"fieldname" : "hours",
			"label": _("Hours"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname" : "amount",
			"label": _("Amount"),
			"fieldtype": "Currency",
			"width": 100
		},
		{
			"fieldname": "cost_center",
			"label": _("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 400
		},
	]
	
	return columns
