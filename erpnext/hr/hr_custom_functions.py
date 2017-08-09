# Copyright (c) 2016, Druk Holding & Investments Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint
from frappe.utils.data import get_first_day, get_last_day, add_days
from erpnext.custom_utils import get_year_start_date, get_year_end_date

##
# Post casual leave on the first day of every month
##
def post_casual_leaves():
	date = add_days(frappe.utils.nowdate(), 10)
	start = get_year_start_date(date);
	end = get_year_end_date(date);
	employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active' and employment_type in (\'Regular\', \'Contract\')", as_dict=True)
	for e in employees:
		la = frappe.new_doc("Leave Allocation")
		la.employee = e.name
		la.employee_name = e.employee_name
		la.leave_type = "Casual Leave"
		la.from_date = str(start)
		la.to_date = str(end)
		la.carry_forward = cint(0)
		la.new_leaves_allocated = flt(10)
		la.submit()

##
# Post earned leave on the first day of every month
##
def post_earned_leaves():
	date = add_days(frappe.utils.nowdate(), -20)
	start = get_first_day(date);
	end = get_last_day(date);
	
	employees = frappe.db.sql("select name, employee_name from `tabEmployee` where status = 'Active' and employment_type in (\'Regular\', \'Contract\')", as_dict=True)
	for e in employees:
		la = frappe.new_doc("Leave Allocation")
		la.employee = e.name
		la.employee_name = e.employee_name
		la.leave_type = "Earned Leave"
		la.from_date = str(start)
		la.to_date = str(end)
		la.carry_forward = cint(1)
		la.new_leaves_allocated = flt(2.5)
		la.submit()

#function to get the difference between two dates
@frappe.whitelist()
def get_date_diff(start_date, end_date):
	if start_date is None:
		return 0
	elif end_date is None:
		return 0
	else:	
		return frappe.utils.data.date_diff(end_date, start_date) + 1;
