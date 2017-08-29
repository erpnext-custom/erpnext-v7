# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def execute(filters=None):
	columns = get_columns();

	data = get_data(filters);
	#data = []
	#for a in datas:
	#	total = flt(a.basic)
	#	frappe.msgprint(str(a))
	for a in data:
		frappe.msgprint(str(a))
	return columns, data

#def get_data(query, filters=None):
	#data = []
	#datas = frappe.db.sql(query, as_dict=True);
	#for d in datas:
		#row = [d.Cost_centere, d.Basic, d.Corporate allow, d.Contract Allow, flt(d.received) - flt(d.issued)]
		#data.append(row);
	#return data
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

	query = ("""select cost_center, SUM(basic), SUM(corporate), SUM(contract), SUM(officiating), SUM(communication), SUM(fuel), SUM(overtime), SUM(psa), SUM(transfer), SUM(housing), SUM(high), SUM(difficult), SUM(shift),SUM(scarcity),SUM(salary), (sum(basic)+sum(corporate)+sum(contract)+sum(officiating)+sum(communication)+sum(fuel)+sum(overtime)+sum(psa)+sum(transfer)+sum(housing)+sum(high)+sum(difficult)+sum(shift)+sum(scarcity)+sum(salary)) as Amount FROM

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
