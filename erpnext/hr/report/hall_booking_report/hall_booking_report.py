# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_data(filters=None):
        query = "select posting_date, customer, hall_type, from_date, to_date, no_of_days, rate, amount, name  from `tabHall Booking` where docstatus = 1 "

        if filters.from_date and filters.to_date:
                query += " and from_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"

        if filters.customer:
                query += " and customer = \'" + str(filters.customer) + "\'"

	if filters.hall_type:
		query += " and hall_type = \'" + str(filters.hall_type) + "\'"

        query += " order by `posting_date` desc"
	data = frappe.db.sql(query)
	
	return data

def get_columns():
        return [
                ("Posting Date") + ":Date:140",
                ("Customer") + ":Link/Customer:100",
                ("Hall Type.") + ":Data:100",
                ("From Date") + ":Date:130",
                ("To Date") + ":date:130",
                ("No of Days") + ":Data:100",
                ("Rate") + ":Currency:100",
                ("Amount") + ":Currency:90",
                ("Reference") + ":Link/Hall Booking:100",
        ]

