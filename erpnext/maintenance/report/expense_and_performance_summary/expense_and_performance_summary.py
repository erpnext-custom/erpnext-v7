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
	start_date = filters.from_date
	end_date = filters.to_date
	data.append(["<b>Expense Head</b>"])
	
	for a in frappe.db.sql("select name from `tabExpense Head` where is_disabled = 0 order by order_index", as_dict=1):
		cond = get_conditions(filters)
		query ="""
			SELECT sum(li.hours) as hours, 
				li.uom, sum(li.initial_reading) as ir 
			FROM `tabLogbook Item` li
			INNER JOIN `tabLogbook` l 
			ON 
				l.name = li.parent 
			INNER JOIN `tabEquipment` e 
			ON e.name = l.equipment 
			WHERE 
				l.docstatus = 1 
			AND 
				l.posting_date 
			BETWEEN '{}' AND '{}'
			AND 
				li.expense_head = '{}' 
			AND 
				l.branch = '{}' 
			{}  
			GROUP BY li.expense_head, li.uom
			""".format(filters.from_date,filters.to_date,a.name,filters.branch,cond)
		# query = "select sum(li.hours) as hours, li.uom, sum(li.initial_reading) as ir from `tabLogbook Item` li, `tabLogbook` l where l.name = li.parent and l.docstatus = 1 and l.posting_date between %(start_date)s and %(end_date)s and li.expense_head = %(expense_head)s and l.equipment = %(eqp)s group by li.expense_head, li.uom"
		res = frappe.db.sql(query,as_dict=1)
		# res = frappe.db.sql(query, {"start_date": start_date, "end_date": end_date, "expense_head": a.name, "eqp": filters.equipment}, as_dict=1)
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
	sch_data = frappe.db.sql("""
	select 
		sum(scheduled_working_hour) as swh 
	from tabLogbook l 
	INNER JOIN 
	 `tabEquipment` e 
	ON e.name = l.equipment 
	WHERE l.docstatus = 1 
	AND	l.posting_date 
	BETWEEN '{}' AND '{}' 
	AND 
		l.branch = '{}' 
	{}""".format(filters.from_date,filters.to_date,filters.branch,cond), as_dict=1)
	# sch_data = frappe.db.sql("select sum(scheduled_working_hour) as swh from tabLogbook where docstatus = 1 and equipment = %(eqp)s and posting_date between %(start_date)s and %(end_date)s", {"eqp": filters.equipment, "start_date": start_date, "end_date": end_date}, as_dict=1)
	if sch_data:
		scheduled = sch_data[0].swh

	data.append(["<b><i>Normal working hours</i></b>", scheduled])	
	for p in frappe.db.sql("select name from `tabDowntime Reason` where type = 'Availability'", as_dict=1):
		query = """
			SELECT 
				sum(di.hours) as hours 
			FROM `tabDowntime Item` di
			INNER JOIN tabLogbook l
			ON l.name = di.parent 
			INNER JOIN `tabEquipment` e 
			ON e.name = l.equipment 
			WHERE l.docstatus = 1 
			AND di.downtime_reason = '{0}' 
			AND l.posting_date between '{1}' 
			AND '{2}' 
			AND l.branch = '{3}' 
			{4}""".format(p.name,filters.from_date,filters.to_date,filters.branch,cond)
		hrs = frappe.db.sql(query, as_dict=1)
		# hrs = frappe.db.sql("select sum(di.hours) as hours from `tabDowntime Item` di, tabLogbook l where l.name = di.parent and l.docstatus = 1 and di.downtime_reason = %(downtime_reason)s and l.posting_date between %(start_date)s and %(end_date)s and l.equipment = %(eqp)s", {"downtime_reason": p.name, "eqp": filters.equipment, "start_date": start_date, "end_date": end_date}, as_dict=1)
		if hrs:
			data.append([p.name, hrs[0].hours])
			performance = flt(performance) + flt(hrs[0].hours)
		else:
			data.append([p.name, 0])
	data.append(["<b><i>Total downtime</i></b>", performance])
	data.append(["<b><i>Availability, hrs</i></b>", flt(scheduled) - flt(performance)])	
	data.append([])

	for p in frappe.db.sql("select name from `tabDowntime Reason` where type = 'Utilization'", as_dict=1):
		hrs = frappe.db.sql("""
			SELECT 
				sum(di.hours) as hours 
			FROM `tabDowntime Item` di
			INNER JOIN `tabLogbook` l 
			ON l.name = di.parent 
			INNER JOIN `tabEquipment` e 
			ON e.name = l.equipment 
			WHERE l.docstatus = 1 
			AND di.downtime_reason = '{}' 
			AND l.posting_date between '{}' 
			AND '{}' 
			AND l.branch = '{}' 
			{}""".format(p.name,filters.from_date,filters.to_date,filters.branch,cond), as_dict=1)
		# hrs = frappe.db.sql("select sum(di.hours) as hours from `tabDowntime Item` di, `tabLogbook` l where l.name = di.parent and l.docstatus = 1 and di.downtime_reason = %(downtime_reason)s and l.posting_date between %(start_date)s and %(end_date)s and l.equipment = %(eqp)s", {"downtime_reason": p.name, "eqp": filters.equipment, "start_date": start_date, "end_date": end_date}, as_dict=1)
		if hrs:
			data.append([p.name, hrs[0].hours])
			availability = flt(availability) + flt(hrs[0].hours)
		else:
			data.append([p.name, 0])

	data.append(["<b><i>Total unproductive time loss, hrs</i></b>", availability])	
	data.append(["<b><i>Utilization</i></b>", flt(scheduled) - flt(performance) - flt(availability)])	
	data.append([])
	for p in frappe.db.sql("select name from `tabOffence`", as_dict=1):
		hrs = frappe.db.sql("""
		SELECT count(1) as no 
		FROM `tabIncident` i 
		INNER JOIN `tabEquipment` e 
			ON e.name = i.equipment 
		WHERE i.docstatus = 1 
		AND i.posting_date 
		BETWEEN '{}' 
		AND '{}' 
		AND e.branch = '{}' 
		{} 
		AND i.offence = '{}'""".format(filters.from_date,filters.to_date,filters.branch,cond,p.name), as_dict=1)
		# hrs = frappe.db.sql("select count(1) as no from `tabIncident` where docstatus = 1 and posting_date between %(start_date)s and  %(end_date)s and equipment = %(eqp)s and offence = %(offence)s", {"start_date": start_date, "end_date": end_date, "eqp": filters.equipment, "offence": p.name}, as_dict=1)
		if hrs:
			data.append([p.name, hrs[0].no])
		else:
			data.append([p.name, 0])
		
	return data

def get_conditions(filters):
	query1 = ""
	query2 = ""
	if filters.from_date > filters.to_date:
		frappe.throw("From Date cannot be greater than To Date")
	if filters.supplier and filters.company_owned:
		frappe.throw("There wont be Vendor for Company owned Equipment")
	if filters.supplier:
		query1 += " AND e.supplier = '{}'".format(filters.supplier)

	if filters.equipment:
		query1+= " AND e.name = '{}'".format(filters.equipment)

	if filters.equipment_type:
		query1 += " AND e.equipment_type = '{}'".format(filters.equipment_type)

	if filters.company_owned:
		query1 += " AND e.not_cdcl = 0"
	return query1

def get_columns():
	return ["Particulars:Data:400", "Hours:Float:100", "Trip:Float:100"]	

