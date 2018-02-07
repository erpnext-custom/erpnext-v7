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
	#for a in data:
		#frappe.msgprint(str(a))
	return columns, data

def get_columns():
	return [
		("Cost Center") + ":Link/Cost Center:120",
		("PF") + ":Currency:120",
		("Salary Tax")+ ":Currency:120",
		("Health Contribution") + ":Currency:120",
		("GIS") +":Currency:120",
		("Salary Advance Deductions") + ":Currency:120",
		("Education Loan")+ ":Currency:120",
		("Sothe") + ":Currency:120",
		("Adhoc Recoveries") + ":Currency:120",
		("Financial Institution Loan") +":Currency:120",
		("SWS")+":Currency:120",
		("Salary Saving Scheme") +":Currency:=120",
		("Other Recoveries") + ":Currency:120",
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
				dates.append(str(a))
	else:
		frappe.throw("From date cannot be grater than To Date")

	query = ("""select cost_center, SUM(ifnull(pf,0)), SUM(ifnull(salary_tax,0)), SUM(ifnull(health_cont,0)), SUM(ifnull(gis,0)), SUM(ifnull(advance_ded,0)), SUM(ifnull(edu_loan,0)), SUM(ifnull(sothe,0)), SUM(ifnull(adhoc_rec,0)), SUM(ifnull(financial_loan,0)), SUM(ifnull(sws,0)), SUM(ifnull(sss,0)),SUM(ifnull(other_rec,0)), SUM((ifnull(pf,0)+ifnull(salary_tax,0)+ifnull(health_cont,0)+ifnull(gis,0)+ifnull(advance_ded,0)+ifnull(edu_loan,0)+ifnull(sothe,0)+ifnull(adhoc_rec,0)+ifnull(financial_loan,0)+ifnull(sws,0)+ifnull(sss,0)+ifnull(other_rec,0))) as Amount FROM
(select (select cost_center from tabEmployee e where e.name = ss.employee) AS cost_center,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'PF') AS pf,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Salary Tax') AS salary_tax,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Health Contribution') AS health_cont,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Group Insurance Scheme') AS gis,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Salary Advance Deductions') AS advance_ded,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Education Loan') AS edu_loan,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Sothe') AS sothe,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Adhoc Recoveries') AS adhoc_rec,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Financial Institution Loan') AS financial_loan,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'SWS') AS sws,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Salary Saving Scheme') AS sss,
(select SUM(sd.amount) FROM `tabSalary Detail` sd WHERE sd.parent = ss.name AND sd.salary_component = 'Other Recoveries') AS other_rec
FROM `tabSalary Slip` ss where ss.docstatus = 1 and ss.branch like %(branch)s and ss.month in %(months)s and ss.fiscal_year = %(fy)s)
AS tab """)

	query += " group by cost_center "

	result = frappe.db.sql(query, {"branch":filters.branch, "months": dates, "fy": filters.fiscal_year})
	#frappe.msgprint(filters.branch)
	#frappe.msgprint("{0}".format(result))
	return result






