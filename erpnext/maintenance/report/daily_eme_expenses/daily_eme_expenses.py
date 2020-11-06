# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, flt, getdate, add_days, formatdate
from frappe import msgprint, _
from calendar import monthrange

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_data(filters):
	data = []
	exp_map = get_eme_expenses()
	actual = ["<b>Total, Actual Hours<b>"]
	scheduled_wh = ["<b>Scheduled Hour</b>"]

	for exp in exp_map:
		exp_row = ["<b>" + str(exp.name) + "</b>"]
		hr_row = ["<b><i>Hours</i></b>"]
		fr = ["<i>FR</i>"]
		ir = ["<i>IR</i>"]
		tar = ["<i>Target Trip</i>"]
		ach = ["<i>Achieved Trip</i>"]
		trip_hour = ["<b><i>Trip Hours</i></b>"]
		total_hr = ["<b>Total Hours<b>"]

		current_date = getdate(filters.from_date)

		while True:
			actual.append(0)
			query = "select max(l.scheduled_working_hour) as swh, sum(li.hours) as hours, li.uom, l.target_trip, min(li.initial_reading) as ir, max(li.final_reading) as fr from `tabLogbook Item` li, tabLogbook l where l.name = li.parent and l.docstatus = 1 and l.posting_date = %(posting_date)s and li.expense_head = %(expense_head)s and l.equipment = %(eqp)s group by li.expense_head, li.uom"
			res = frappe.db.sql(query, {"posting_date": current_date, "expense_head": exp.name, "eqp": filters.equipment}, as_dict=1)
			total_hour = 0
			if res:
				for a in res:
					if a.uom == "Hour":	
						hr_row.append(a.hours)
						fr.append(a.fr)
						ir.append(a.ir)
						#keep default
						tar.append("")
						ach.append("")
						trip_hour.append(0)
					else:
						#keep default
						hr_row.append(0)
						fr.append("")
						ir.append("")
						#change
						tar.append(a.target_trip)
						ach.append(a.ir)
						trip_hour.append(a.hours)
					total_hour =  flt(total_hour) + flt(a.hours)
				total_hr.append(total_hour)
			else:
				hr_row.append(0)
				fr.append("")
				ir.append("")
				tar.append("")
				ach.append("")
				trip_hour.append(0)
				total_hr.append(0)
			
			current_date = add_days(current_date, 1)
			if current_date > getdate(filters.to_date):
				break

		data.append(exp_row)
		data.append(hr_row)
		data.append(ir)
		data.append(fr)
		data.append(trip_hour)
		data.append(tar)
		data.append(ach)
		data.append(total_hr)
		data.append([])
		
		for a in range(len(total_hr)):
			if a == 0:
				continue
			actual[a] = flt(actual[a]) + flt(total_hr[a])
	data.append(actual)

	current_date = getdate(filters.from_date)

	ava_data = {}
	per_data = {}
	util_data = {}
	downtime_record = ["<b><i>Total Downtime</b></i>"]
	total_unproductive = ["<b><i>Total unproductive time loss</b></i>"]

	while True:
		sch_work_hour = frappe.db.sql("select max(scheduled_working_hour) as swh from tabLogbook where docstatus = 1 and posting_date = %(posting_date)s and equipment = %(eqp)s", {"posting_date": current_date, "eqp": filters.equipment}, as_dict=1)
		if sch_work_hour:
			scheduled_wh.append(sch_work_hour[0].swh)
		else:
			scheduled_wh.append(0)
		total_perf = 0
		for p in frappe.db.sql("select name from `tabDowntime Reason` where type = 'Availability'", as_dict=1):
			if p.name not in per_data.keys():
				per_data[p.name] = [p.name]
			
			hrs = frappe.db.sql("select sum(di.hours) as hours, max(l.scheduled_working_hour) as swh from `tabDowntime Item` di, tabLogbook l where l.name = di.parent and l.docstatus = 1 and di.downtime_reason = %(downtime_reason)s and l.posting_date = %(posting_date)s and l.equipment = %(eqp)s", {"downtime_reason": p.name, "eqp": filters.equipment, "posting_date": current_date}, as_dict=1)
			if hrs:
				per_data[p.name].append(hrs[0].hours)
				total_perf = flt(total_perf) + flt(hrs[0].hours)
			else:
				per_data[p.name].append(0)

		total_ava = 0
		for p in frappe.db.sql("select name from `tabDowntime Reason` where type = 'Utilization'", as_dict=1):
			if p.name not in ava_data.keys():
				ava_data[p.name] = [p.name]
			
			hrs = frappe.db.sql("select sum(di.hours) as hours from `tabDowntime Item` di, tabLogbook l where l.name = di.parent and l.docstatus = 1 and di.downtime_reason = %(downtime_reason)s and l.posting_date = %(posting_date)s and l.equipment = %(eqp)s", {"downtime_reason": p.name, "eqp": filters.equipment, "posting_date": current_date}, as_dict=1)
			if hrs:
				ava_data[p.name].append(hrs[0].hours)
				total_ava = flt(total_ava) + flt(hrs[0].hours)
			else:
				ava_data[p.name].append(0)
	

		for p in frappe.db.sql("select name from `tabOffence`", as_dict=1):
			if p.name not in util_data.keys():
				util_data[p.name] = [p.name]
			hrs = frappe.db.sql("select count(1) as no from tabIncident where docstatus = 1 and posting_date = %(posting_date)s and equipment = %(eqp)s and offence = %(offence)s", {"posting_date": current_date, "eqp": filters.equipment, "offence": p.name}, as_dict=1)
			if hrs:
				util_data[p.name].append(hrs[0].no)
			else:
				util_data[p.name].append(0)


		total_unproductive.append(total_ava)
		downtime_record.append(total_perf)
		current_date = add_days(current_date, 1)
		if current_date > getdate(filters.to_date):
			break

	availability = ["<b><i>Availability (Row 76 - 79)</b></i>"]
	utilization = ["<b><i>Utilization (Row 80 - 89)</b></i>"]

	data.append([])
	data.append(["<b>Performance Record</b>"])
	data.append(scheduled_wh)

	for a in per_data:
		data.append(per_data[a])
	data.append(downtime_record)
	"""Scheduled time - total downtime"""
	for a in range(1, len(downtime_record)):
		availability.append(flt(scheduled_wh[a]) - flt(downtime_record[a]))
	data.append(availability)
	data.append([])
	for a in ava_data:
		data.append(ava_data[a])
	data.append(total_unproductive)
	"""Scheduled time - total downtime - total_unproductive"""
	for a in range(1, len(scheduled_wh)):
		utilization.append(flt(availability[a]) - flt(total_unproductive[a]))
	data.append(utilization)
	data.append([])
	for a in util_data:
		data.append(util_data[a])
	data.append([])

	return data

def get_columns(filters):
	columns = ["Expense Head/Reading::200"]

	if filters.from_date and filters.to_date:
		if getdate(filters.from_date) > getdate(filters.to_date):
			frappe.throw("From Date should not be grater than To Date")
		current_date = getdate(filters.from_date)
		while True:
			columns.append(str(formatdate(current_date, 'dd/MM/yyyy')) + "::90")
			current_date = add_days(current_date, 1)
			if current_date > getdate(filters.to_date):
				break
	else:
		frappe.throw("From Date and To Date are mandatory")

	return columns

def get_eme_expenses():
	query = "select name, abbr from `tabExpense Head` where is_disabled = 0 order by order_index"
	return frappe.db.sql(query, as_dict=1)

def get_per_ava():
	query = "select name, type as reason_type from `tabDowntime Reason` order by type"
	return frappe.db.sql(query, as_dict=1)


