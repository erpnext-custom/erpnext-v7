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
		select ti.name, ti.tenant_name,
			GROUP_CONCAT(DISTINCT(rpi.rental_bill) SEPARATOR ' ') rental_bill,
			(count(rpi.name) * rpi.rent_received) rental_income,
			sum(rpi.rent_received),
			sum(rpi.pre_rent_amount),
			sum(rb.adjusted_amount),
			sum(rpi.excess_amount),
			sum(rpi.tds_amount),
			sum(rpi.penalty),
			sum(rpi.discount_amount),

			(sum(rpi.rent_received) + sum(rpi.pre_rent_amount) + sum(rpi.penalty) + sum(rpi.excess_amount) - sum(rpi.tds_amount) - sum(rpi.discount_amount)) total_rent_received,
			
			(sum(rpi.bill_amount) - sum(rpi.rent_received) - sum(rb.adjusted_amount)) outstanding_bill,
			(sum(rpi.pre_rent_amount) - sum(rb.adjusted_amount)) pre_rent_balance
		from `tabTenant Information` ti
		INNER JOIN `tabRental Payment Item` as rpi ON ti.name = rpi.tenant AND rpi.docstatus = 1
		INNER JOIN `tabRental Payment` rp ON rp.name = rpi.parent
		INNER JOIN `tabRental Bill` as rb ON rb.tenant = ti.name
			
		where rb.posting_date between '{from_date}' and '{to_date}' {cond}
		group by ti.name
		order by ti.name
	""".format(from_date=filters.get("from_date"), to_date=filters.get("to_date"), cond=conditions))

	# where rb.allocation_date between {from_date} and {to_date} {cond}
	# innerjoin `tabRental Bill` rb ON rb.tenant = ti.name