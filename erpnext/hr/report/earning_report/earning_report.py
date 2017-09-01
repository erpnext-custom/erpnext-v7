# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns();

	data = get_data(filters);
	#data = []
	data = []
	for d in datas:
		total = [d.cost_centere, flt(d.a), flt(d.b), flt(d.c), flt(d.d),flt(d.e),flt(d.f),flt(d.g),flt(d.h),flt(d.i),flt(d.j),flt(d.k),flt(d.l), flt(d.m), flt(d.n),flt(d.o),  flt(d.a)+flt(d.b)+flt(d.c)+flt(d.d)+flt(d.e)+flt(d.f)+flt(d.g)+flt(d.h)+flt(d.i)+flt(d.j)+flt(d.k)+flt(d.l)+flt(d.m)+flt(d.n)+flt(d.o)]
	data.append(row);
	return coulumns, data

def get_columns():
	return [
		("Cost Center") + ":Link/Cost Center:120",
		("Basic Pay") + ":Currency:100",
		("Coporate Allowance")+ ":Currency:80",
		("Contract Allow.") + ":Cureency:80",
		("Officiating Allow.") +":Currency:80",
		("Communication Allow.")+":Currency:80",
		("Fuel Allow.") +":Currency:80",
		("Overtime Allow.") +":Currency:=80",
		("PSA Allow.") + ":Currency:80",
		("Transfer Allow.") + ":Currency:80",
		("Housing  Allow.") + ":Currency:80",
		("High Altitude Allow.")+ ":Currency:80",
		("Difficult Allow.") + ":Currency:80",
		("Shift Allow.") + ":Currency:80",
		("Scarcity  Allow.") +":Currency:80",
		("Salary Arrears ") +":Currency:80",
		("Amount") + ":Currency:120"
	]

def get_data(filters):
	if not filters.branch:
		filters.branch = '%'
	from_month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(filters["from_date"])
	to_month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(filters["to_date"])
	if from_month <= to_month:
		dates = []
		for a in range (from_month+1, to_month+2):
			if a < 10:
				dates.append('0'+ str(a))
	else:
		frappe.throw("From date cannot be grater than To Date")

	query = ("""select cost_center, SUM(basic)as a, SUM(corporate)as b, SUM(contract)as c, SUM(officiating)as d, SUM(communication)as e, SUM(fuel)as f, SUM(overtime)as g, SUM(psa)as h, SUM(transfer)as i, SUM(housing)as j, SUM(high)as k, SUM(difficult)as l, SUM(shift)as m,SUM(scarcity)as n,SUM(salary)as o FROM
(select (select cost_center from tabEmployee e where e.name = ss.employee) AS cost_center,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Basic Pay') AS basic,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Corporate Allowance') AS corporate,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Contract Allowance') AS contract,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Officiating Allowance') AS officiating,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Communication Allowance') AS communication,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Fuel Allowance') AS fuel,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Overtime Allownace') AS overtime,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'PSA') AS psa,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Transfer Allowance') AS transfer,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Housing allowance') AS housing,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'High Altitude allowance') AS high,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Difficult area allowance') AS difficult,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Shift Allowance') AS shift,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Scarcity Allowance') AS scarcity,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Salary Arrears') AS salary
FROM `tabSalary Slip` ss where ss.docstatus = 1 and ss.branch like %(branch)s and ss.month in %(months)s and ss.fiscal_year = %(fy)s)
AS tab """)

	query += " group by cost_center "
	return frappe.db.sql(query, {"branch":filters.branch, "months": dates, "fy": filters.fiscal_year})
