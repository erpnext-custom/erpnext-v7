# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns();
	data = get_data(filters);
	return columns, data

def get_columns():
	return [
		("Tenant Code") + ":Data:120",
		("Tenant") + ":Data:150",
		("Rental Bill") + ":Data:260",
		("Rental Income") + ":Currency:120",
		("Rent Received") + ":Currency:120",
		("Pre-rent") + ":Currency:120",
		("Adjusted Amount") + ":Currency:120",
		("Excess Rent") + ":Currency:120",
		("TDS") + ":Currency:90",
		("Penalty") + ":Currency:90",
		("Discount") + ":Currency:90",
		("Total Rent Received") + ":Currency:120",
		("Outstanding Rent") + ":Currency:120",
		("Pre-rent Balance") + ":Currency:120"
	]

def get_condition(filters):
	condition = ''
	# if filters.get("tenant_type") != '':
	# 	if filters.get("tenant_type") == "NHDCL Employee":
	# 		condition += " and ti.is_nhdcl_employee = 1 "
	# 	if filters.get("tenant_type") == "Others":
	# 		condition += " and ti.is_nhdcl_employee = 0 "
	if filters.get("rental_official"):
		if filters.get("rental_official") == 'Dorji Wangmo': 
			# two dorji wangmo in the system. use the below
			official = "NHDCL1905030"
		else: 
			emp = frappe.db.sql("select name from tabEmployee where employee_name = '{}'".format(filters.get("rental_official")), as_dict=True)
			official = emp[0].name
		condition += " and rp.rental_official = '{0}'".format(official)
	
	return condition

def get_data(filters):
	conditions = get_condition(filters);
	return frappe.db.sql(""" 
		select rb.tenant, rb.tenant_name,
			GROUP_CONCAT(DISTINCT(rb.name) SEPARATOR ' ') rental_bill,
			(count(rb.name) * rb.rent_amount) rental_income,
			sum(rb.received_amount),
			sum(rb.pre_rent_amount),
			sum(rb.adjusted_amount),
			sum(rpi.excess_amount),
			sum(rb.tds_amount),
			sum(rb.penalty),
			sum(rb.discount_amount),

			(sum(rb.received_amount) + sum(rb.pre_rent_amount) + sum(rb.penalty) + sum(rpi.excess_amount) - sum(rb.tds_amount) - sum(rb.discount_amount)) total_rent_received,
			
			(sum(rb.receivable_amount) - sum(rb.received_amount) - sum(rb.adjusted_amount)) outstanding_bill,
			(sum(rb.pre_rent_amount) - sum(rb.adjusted_amount)) pre_rent_balance
		from `tabRental Bill` rb
		LEFT JOIN `tabRental Payment Item` as rpi ON rb.name = rpi.rental_bill AND rpi.docstatus = 1
		
		where rb.docstatus=1 and rb.posting_date between '{from_date}' and '{to_date}' {cond}
		group by rb.tenant
		order by rb.tenant
	""".format(from_date=filters.get("from_date"), to_date=filters.get("to_date"), cond=conditions))

	# where rb.allocation_date between {from_date} and {to_date} {cond}
	# innerjoin `tabRental Bill` rb ON rb.tenant = ti.name