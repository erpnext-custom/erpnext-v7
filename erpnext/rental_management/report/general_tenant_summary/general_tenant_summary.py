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
	if filters.get("tenant_type") != '':
		if filters.get("tenant_type") == "NHDCL Employee":
			condition += " and ti.is_nhdcl_employee = 1 "
		if filters.get("tenant_type") == "Others":
			condition += " and ti.is_nhdcl_employee = 0 "
	return condition

def get_data(filters):
	conditions = get_condition(filters);
	return frappe.db.sql(""" 
		select ti.name, ti.tenant_name,
			GROUP_CONCAT(CONCAT('<a href="desk#Form/Rental Bill/',rb.name,'"> ',rb.name,'</a>' )) rental_bill,
			(count(rb.name) * rb.received_amount) rental_income,
			sum(rb.received_amount),
			sum(rb.pre_rent_amount),
			sum(rb.adjusted_amount),
			(
				select sum(rpi.excess_amount) from `tabRental Payment Item` rpi
				inner join `tabRental Payment` rp ON rp.name=rpi.parent
				where rp.docstatus=1 and rpi.tenant=ti.name and rp.posting_date between '{from_date}' and '{to_date}'
			) excess_rent,
			sum(rb.tds_amount),
			sum(rb.penalty),
			sum(rb.discount_amount),

			(sum(rb.received_amount) + sum(rb.pre_rent_amount) + sum(rb.penalty)
			+ (
				select sum(rpi.excess_amount) from `tabRental Payment Item` rpi
				inner join `tabRental Payment` rp ON rp.name=rpi.parent
				where rp.docstatus=1 and rpi.tenant=ti.name and rp.posting_date between '{from_date}' and '{to_date}'
			)
			- sum(rb.tds_amount) - sum(rb.discount_amount)) total_rent_received,
			
			(sum(rb.rent_amount) - sum(rb.received_amount)) outstanding_bill,
			(sum(rb.pre_rent_amount) - sum(rb.adjusted_amount)) pre_rent_balance
		from `tabTenant Information` ti
		inner join `tabRental Bill` rb ON rb.tenant = ti.name
		inner join `tabRental Bill Received` rbr ON rbr.parent = rb.name
		
		where rb.posting_date between '{from_date}' and '{to_date}' {cond}
		group by ti.name
		order by ti.name
	""".format(from_date=filters.get("from_date"), to_date=filters.get("to_date"), cond=conditions))

	# where rb.allocation_date between {from_date} and {to_date} {cond}
	# innerjoin `tabRental Bill` rb ON rb.tenant = ti.name