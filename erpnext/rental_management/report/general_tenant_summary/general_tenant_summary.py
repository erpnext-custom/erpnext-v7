# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns();
	if filters.get("rental_official"):
		data = get_tenant_list(filters);
	else:
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
		("Rent Write-off") + ":Currency:100",
		("Penalty") + ":Currency:90",
		("Discount") + ":Currency:90",
		("Total Rent Received") + ":Currency:120",
		("Outstanding Rent") + ":Currency:120",
		("Pre-rent Balance") + ":Currency:120"
	]

def get_tenant_list(filters):
	official=''
	if filters.get("rental_official"):
		if filters.get("rental_official") == 'Dorji Wangmo': 
			# two dorji wangmo in the system. use the below
			official = "NHDCL1905030"
		else: 
			emp = frappe.db.sql("select name from tabEmployee where employee_name = '{}'".format(filters.get("rental_official")), as_dict=True)
			official = emp[0].name
	tenant_list = frappe.db.sql("""
		Select ti.name, tro.from_date,
				Case
					When (select idx from `tabTenant Rental Officials` where parent=ti.name and from_date > tro.from_date)
						Then (select from_date as to_date from `tabTenant Rental Officials` where parent=ti.name and idx=tro.idx + 1)
					Else '{end_date}' 
				End as to_date
		From `tabTenant Information` ti
		Inner Join `tabTenant Rental Officials` tro On ti.name = tro.parent 
		Where tro.rental_official = '{rental_official}'""".format(rental_official=official, end_date=filters.get("to_date")), as_dict=1)

	data = []
	for i in tenant_list:
		datas = get_official_tenant_data(tenant=i.name,from_date=i.from_date,to_date=i.to_date)
		for d in datas:
			row = [d.tenant,d.tenant_name,d.rental_bill,d.rental_income,d.received_amount,d.pre_rent_amount,d.adjusted_amount,d.excess_amount,
				d.tds_amount,d.rent_write_off_amount,d.penalty,d.discount_amount,d.total_rent_received,d.outstanding_bill,d.pre_rent_balance]
			data.append(row)

	return data

def get_official_tenant_data(tenant,from_date,to_date):
	return frappe.db.sql(""" 
		select rb.tenant, rb.tenant_name,
			GROUP_CONCAT(DISTINCT(rb.name) SEPARATOR ' ') rental_bill,
			(count(rb.name) * rb.rent_amount) rental_income,
			sum(rb.received_amount) received_amount,
			sum(rb.pre_rent_amount) pre_rent_amount,
			sum(rb.adjusted_amount) adjusted_amount,
			sum(rpi.excess_amount) excess_amount,
			sum(rb.tds_amount) tds_amount,
			sum(rb.rent_write_off_amount) rent_write_off_amount,
			sum(rb.penalty) penalty,
			sum(rb.discount_amount) discount_amount,

			(sum(rb.received_amount) + sum(rb.pre_rent_amount) + sum(rb.penalty) + sum(rpi.excess_amount) - sum(rb.tds_amount) - sum(rb.discount_amount)) total_rent_received,
			
			(sum(rb.receivable_amount) - sum(rb.received_amount) - sum(rb.adjusted_amount) - sum(rb.rent_write_off_amount)) outstanding_bill,
			(sum(rb.pre_rent_amount) - sum(rb.adjusted_amount)) pre_rent_balance
		from `tabRental Bill` rb
		LEFT JOIN `tabRental Payment Item` as rpi ON rb.name = rpi.rental_bill
		
		where rb.docstatus=1 and rb.posting_date between '{0}' and '{1}' and rb.tenant='{2}'
		group by rb.tenant
		order by rb.tenant
	""".format(from_date, to_date, tenant), as_dict=1)

def get_condition(filters):
	condition = ''
	if filters.get("rental_official"):
		if filters.get("rental_official") == 'Dorji Wangmo': 
			# two dorji wangmo in the system. use the below
			official = "NHDCL1905030"
		else: 
			emp = frappe.db.sql("select name from tabEmployee where employee_name = '{}'".format(filters.get("rental_official")), as_dict=True)
			official = emp[0].name
		condition += " and tro.rental_official = '{0}'".format(official)
	
	return condition

def get_data(filters):
	# conditions = get_condition(filters);
	conditions = '';
	return frappe.db.sql(""" 
		select rb.tenant, rb.tenant_name,
			GROUP_CONCAT(DISTINCT(rb.name) SEPARATOR ' ') rental_bill,
			(count(rb.name) * rb.rent_amount) rental_income,
			sum(rb.received_amount),
			sum(rb.pre_rent_amount),
			sum(rb.adjusted_amount),
			sum(rpi.excess_amount),
			sum(rb.tds_amount),
			sum(rb.rent_write_off_amount),
			sum(rb.penalty),
			sum(rb.discount_amount),

			(sum(rb.received_amount) + sum(rb.pre_rent_amount) + sum(rb.penalty) + sum(rpi.excess_amount) - sum(rb.tds_amount) - sum(rb.discount_amount)) total_rent_received,
			
			(sum(rb.receivable_amount) - sum(rb.received_amount) - sum(rb.adjusted_amount) - sum(rb.rent_write_off_amount)) outstanding_bill,
			(sum(rb.pre_rent_amount) - sum(rb.adjusted_amount)) pre_rent_balance
		from `tabRental Bill` rb
		LEFT JOIN `tabRental Payment Item` as rpi ON rb.name = rpi.rental_bill
		
		where rb.docstatus=1 and rb.posting_date between '{from_date}' and '{to_date}' {cond}
		group by rb.tenant
		order by rb.tenant
	""".format(from_date=filters.get("from_date"), to_date=filters.get("to_date"), cond=conditions))
