# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns();

	data = get_data(filters);

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
		("Basic Pay") + ":Float:100",
		("Coporate Allowance")+ ":Float:80",
		("Contract Allow.") + ":Float:80",
		("Officiating Allow.") +":Float:80",
		("Communication Allow.")+":Float:80",
		("Fuel Allow.") +":Float:80",
		("Overtime Allow.") +":Float:=80",
		("PSA Allow.") + ":Float:80",
		("Transfer Allow.") + ":Float:80",
		("Housing  Allow.") + ":Float:80",
		("High Altitude Allow.")+ ":Float:80",
		("Difficult Allow.") + ":Float:80",
		("Shift Allow.") + ":Float:80",
		("Scarcity  Allow.") +":Float:80",
		("Salary Arrears ") +":Data:80",
		("Amount") + ":Data:120"
	]

def get_data(filters):

	query = ("""select cost_center, SUM(basic), SUM(corporate), SUM(contract), SUM(officiating), SUM(communication), SUM(fuel), SUM(overtime), SUM(psa), SUM(transfer), SUM(housing), SUM(high), SUM(difficult), SUM(shift),SUM(scarcity),SUM(salary), (sum(basic)+sum(corporate)+sum(contract)+sum(officiating)+sum(communication)+sum(fuel)+sum(overtime)+sum(psa)+sum(transfer)+sum(housing)+sum(high)+sum(difficult)+sum(shift)+sum(scarcity)+sum(salary)) as Amount FROM

(select (select e.cost_center FROM tabEmployee e WHERE e.name = ss.employee) AS cost_center,
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
FROM `tabSalary Slip` ss)
AS tab """)

	if filters.get("branch"):
		query += " and ss.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		month = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(filters["from_date"])
		filter["from_date"] = month
		filter["to_date"] = month
		query += " and month between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	if filters.get("fiscal_year"):
		query += " and ss.fiscal_year = \'" + str(filters.fiscal_year) + "\'"
	query += " group by cost_center "
	return frappe.db.sql(query)
