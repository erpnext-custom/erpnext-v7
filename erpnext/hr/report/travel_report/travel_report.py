#Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns =get_columns()
	data =get_data(filters)
	return columns, data

def get_columns():
	return [
		("Employee") + ":Link/Employee:120",
		("TC Name") + ":Link/Travel Claim:120",
		("Employee Name") + ":data:120",
		("Designation")+":data:120",
		("Cost Center") + ":data:160",
		("Department") + ":data:160",
		("From Date")+":Date:100",
		("To Date")+":Date:100",
		("Claim Month")+":Data:90",
		("DSA Per Day")+":Currency:120",
		("Total Claim")+":Currency:120"
	]

def get_data(filters):
	query ="""select tc.employee as emp, tc.name as n, tc.employee_name as emp_nam, e.designation as des, e.cost_center as cc, 
                       	tc.department as dep, min(tci.date) as frm, max(tci.till_date, tci.date) as too, 
			case month(tc.posting_date) 
			when 1 then "January" when 2 then "Feb" when 3 then "March" when 4 then "April" when 5 then "May" 
			when 6 then "June" when 7 then "July" when 8 then "Auguest" when 9 then "September" 
			when 10 then "October" when 11 then "November"  when 12 then "December" end as mon,
			tc.dsa_per_day as rate, 
                        tc.total_claim_amount as claim
                        from `tabEmployee` e, `tabTravel Claim` tc, `tabTravel Claim Item` tci 
                        where e.name = tc.employee and tc.name = tci.parent and tc.docstatus = 1"""
	if filters.get("employee"):
		query += " and tc.employee = \'" + str(filters.employee) + "\'"

	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov","Dec"].index(filters["month"]) + 1
  		filters["month"] = month
  		query += " and month(tc.posting_date) = {0}".format(filters.get("month"))

	if filters.get("fiscal_year"): 
		query += " and year(tc.posting_date) = {0}".format(filters.get("fiscal_year"))

	if filters.get("cost_center"):
		query += " and e.cost_center = \'" + str(filters.cost_center) + "\'"
	query += " group by tc.name"
	#frappe.msgprint("{0}".format(query))
	return frappe.db.sql(query)

