# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
        cols = [
                _("OT Name") + ":Link/Overtime Application:120",
		_("Branch") + ":Link/Branch:120",
		_("Posting Date") + ":Date:90",
		_("Employee ID") + ":Link/Employee:120",
                _("Employee Name") + ":Data:120",
                _("Designation") + ":Data:120",
                _("Department") + ":Data:160",
                _("Bank") + ":Link/Financial Institution:120",
		_("Account No") + ":Data:120",
		_("Hourly Rate") + ":Data:90",
                _("Total Hour") + ":Int:80",
                _("Total Amount") + ":Currency:100",
                _("Purpose(Regular)") + ":Data:160",
		_("Payment Voucher") + ":Link/Journal Entry:120",
		_("Payment Status") + ":Data:120",
        ]
        return cols


def get_data(filters):
	data = []
	data1 = []
	query =  """ select ot.name, ot.branch, ot.posting_date, ot.employee, ot.employee_name, ot.bank_name, ot.bank_no,
			(select e1.designation from `tabEmployee` e1 where e1.name = ot.employee) as designation,
			(select e2.department from `tabEmployee` e2 where e2.name = ot.employee) as department, ot.rate, ot.total_hours, 
			ot.total_amount, ot.purpose, ot.payment_jv, ot.overtime_payment
			from `tabOvertime Application` ot where ot.docstatus =1"""
	if filters.employee:
		query += " and ot.employee = '{0}'".format(filters.employee)
	# if filters.cost_center:
	# 	query += " and ot.branch = '{0}'".format(filters.branch)
	if filters.from_date and filters.to_date:
		query += " and ot.posting_date between '{0}' and '{1}'".format(filters.from_date, filters.to_date)
	if filters.branch:
		query += " AND ot.branch = '{}'".format(filters.branch)
		
	for d in frappe.db.sql(query, as_dict = True):
		jv_no = ""
		status="Not Paid"
		if d.payment_jv:
			status = payment_status(d.payment_jv)
			jv_no = d.payment_jv
		elif d.overtime_payment:
			status = "Not Paid"
			doc_status = frappe.db.get_value("Overtime Payment", d.overtime_payment, "docstatus")
			if doc_status == 1:
				status = "Paid"
			jv_no = d.overtime_payment

		row1 = [d.name, d.branch, d.posting_date, d.employee, d.employee_name, d.designation, d.department,d.bank_name, d.bank_no, d.rate, d.total_hours, \
		d.total_amount, d.purpose, jv_no, status]
		data.append(row1)

	return data

def payment_status(payment_jv):
	status = 'Not Paid'
	if payment_jv:
		jv = frappe.get_doc("Journal Entry", payment_jv).docstatus
		if jv == 1:
			status  = 'Paid'
	return status
