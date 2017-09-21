# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange

def execute(filters=None):
	if not filters: filters = {}

	filters = get_filters(filters)
	columns = get_columns(filters)
	#att_map = get_attendance_list(conditions, filters)
	eqp_map = get_equipment_details(filters)

	data = []
	filters.month = str(filters.month) if cint(filters.month) > 9 else str("0" + str(filters.month))
	for e in eqp_map:
		if not filters.equipment_type:
			row = [e.name, e.equipment_number, e.equipment_type]
		else:
			row = [e.name, e.equipment_number]

		for day in range(filters["total_days_in_month"]):
			day = str(day + 1) if day + 1 > 9 else str("0" + str(day + 1))
			res = frappe.db.sql("select reason, hours from `tabEquipment Reservation Entry` where docstatus = 1 and equipment = %s and %s between from_date and to_date order by reason desc", (e.name, str(str(filters.year) + "-" + str(filters.month) + "-" + str(day))), as_dict=True)
			if res:
				v = ""
				if res[0].reason == "Maintenance":
					v = "M"
				else:
					if cint(res[0].hours) > 8:
						v = "8"
					elif cint(res[0].hours) > 0:
						total = 0
						for a in res: 
							total+=cint(a.hours)
						v = str(total)
					else:
						v = ""
				row.append(v)
			else:
				row.append("")	
		data.append(row)

		legend = "M = Under Maintenance"

	return columns, data, legend

def get_columns(filters):
	if not filters.equipment_type:
		columns = [
			_("Eqp. Name") + "::140", _("Reg. Number")+ "::140", _("Eqp. Type")+ "::140"
		]
	else:
		columns = [
			_("Eqp. Name") + "::140", _("Reg. Number")+ "::140"
		]

	for day in range(filters["total_days_in_month"]):
		columns.append(cstr(day+1) +"::20")

	return columns

def get_filters(filters):
	if not (filters.get("month") and filters.get("year")):
		msgprint(_("Please select month and year"), raise_exception=1)

	filters["month"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"].index(filters.month) + 1

	filters["total_days_in_month"] = monthrange(cint(filters.year), filters.month)[1]

	return filters

def get_equipment_details(filters):
	query = "select name, equipment_number, equipment_type from `tabEquipment` where is_disabled != 1 and branch = \'"+str(filters.branch)+"\'"
	if filters.equipment_type:
		query += " and equipment_type = \'"+ str(filters.equipment_type) +"\'"
	return frappe.db.sql(query, as_dict=1)

