# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	data = []
	if not filters.year:
		frappe.throw("Year is mandatory")
	start_date = str(filters.year) + "-01-01"
	end_date = str(filters.year) + "-12-31"
	data.append(["<b>Expense Head</b>"])
	
	for a in frappe.db.sql("select name from `tabExpense Head` where is_disabled = 0 order by order_index", as_dict=1):
		query = "select sum(li.hours) as hours, li.uom, sum(li.initial_reading) as ir from `tabLogbook Item` li, tabLogbook l where l.name = li.parent and l.docstatus = 1 and l.posting_date between %(start_date)s and %(end_date)s and li.expense_head = %(expense_head)s and l.equipment = %(eqp)s group by li.expense_head, li.uom"
		res = frappe.db.sql(query, {"start_date": start_date, "end_date": end_date, "expense_head": a.name, "eqp": filters.equipment}, as_dict=1)
		total_hr = 0
		trip = 0
		days = 0
		for exp in res:
			total_hr = flt(exp.hours) + flt(total_hr)
			if exp.uom == "Trip":
				trip = exp.ir
		data.append([a.name, total_hr, trip])
		
	data.append([])
	data.append(["<b>Performance Record</b>"])	

	availability = 0
	performance = 0
	scheduled = 0

	sch_data = frappe.db.sql("select sum(scheduled_working_hour) as swh from tabLogbook where docstatus = 1 and equipment = %(eqp)s and posting_date between %(start_date)s and %(end_date)s", {"eqp": filters.equipment, "start_date": start_date, "end_date": end_date}, as_dict=1)
	if sch_data:
		scheduled = sch_data[0].swh

	data.append(["<b><i>Normal working hours</i></b>", scheduled])	
	for p in frappe.db.sql("select name from `tabDowntime Reason` where type = 'Availability'", as_dict=1):
		hrs = frappe.db.sql("select sum(di.hours) as hours from `tabDowntime Item` di, tabLogbook l where l.name = di.parent and l.docstatus = 1 and di.downtime_reason = %(downtime_reason)s and l.posting_date between %(start_date)s and %(end_date)s and l.equipment = %(eqp)s", {"downtime_reason": p.name, "eqp": filters.equipment, "start_date": start_date, "end_date": end_date}, as_dict=1)
		if hrs:
			data.append([p.name, hrs[0].hours])
			performance = flt(performance) + flt(hrs[0].hours)
		else:
			data.append([p.name, 0])
	data.append(["<b><i>Total downtime</i></b>", performance])
	data.append(["<b><i>Availability, hrs</i></b>", flt(scheduled) - flt(performance)])	
	data.append([])

	for p in frappe.db.sql("select name from `tabDowntime Reason` where type = 'Utilization'", as_dict=1):
		hrs = frappe.db.sql("select sum(di.hours) as hours from `tabDowntime Item` di, tabLogbook l where l.name = di.parent and l.docstatus = 1 and di.downtime_reason = %(downtime_reason)s and l.posting_date between %(start_date)s and %(end_date)s and l.equipment = %(eqp)s", {"downtime_reason": p.name, "eqp": filters.equipment, "start_date": start_date, "end_date": end_date}, as_dict=1)
		if hrs:
			data.append([p.name, hrs[0].hours])
			availability = flt(availability) + flt(hrs[0].hours)
		else:
			data.append([p.name, 0])

	data.append(["<b><i>Total unproductive time loss, hrs</i></b>", availability])	
	data.append(["<b><i>Utilization</i></b>", flt(scheduled) - flt(performance) - flt(availability)])	
	data.append([])
	for p in frappe.db.sql("select name from `tabOffence`", as_dict=1):
		hrs = frappe.db.sql("select count(1) as no from tabIncident where docstatus = 1 and posting_date between %(start_date)s and  %(end_date)s and equipment = %(eqp)s and offence = %(offence)s", {"start_date": start_date, "end_date": end_date, "eqp": filters.equipment, "offence": p.name}, as_dict=1)
		if hrs:
			data.append([p.name, hrs[0].no])
		else:
			data.append([p.name, 0])
		
	return data


def get_columns():
	return ["Particulars::230", "Hours::100", "Trip::100"]	

