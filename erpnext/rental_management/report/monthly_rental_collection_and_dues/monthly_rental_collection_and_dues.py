# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

########### Created by Cheten Tshering on 05/10/2020 #################################

from __future__ import unicode_literals
from frappe.utils.data import get_first_day, get_last_day, add_days
import frappe

def execute(filters):
	if filters.get("amount_receivable") == "Amount Received":
		column, data = get_columns(filters), get_data(filters)
		return column, data
	else:
		columns, data = get_receivable_columns(filters), get_receivable_data(filters)
		return columns, data

def get_receivable_columns(filters):
	columns = [
		("Rental Bill No.") + ":Link/Rental Bill:150",
		("Tenant Name") + "::150",
		("Tenant CID") + ":Link/Tenant Information:150",
		("Posting Date") + ":Date:100",
		("Rent Amount") + ":Currency:100",
		("Received Amount") + ":Currency:100",
		("Receivable Amount") + ":Currency:100",
		("Dzongkhag") + "::100",
		("Location") + "::100",
		("Department") + "::100"
	]
	return columns

def get_receivable_data(filters):
	conds = rbb_conditions(filters)
	data = frappe.db.sql("""
			select
				rb.name,
				rb.tenant_name,
				ti.cid,
				rb.posting_date,
				rb.rent_amount,
				rb.received_amount,
				rb.receivable_amount,
				rb.dzongkhag,
				rb.location,
				rb.department
			from `tabRental Bill` rb, `tabTenant Information` ti
			where rb.docstatus = 1 and rb.tenant=ti.name 
			and (
				(rb.received_amount = 0 and rb.receivable_amount > 0) 
 				or (rb.rental_payment is NULL and rb.receivable_amount > 0) 
				or (rb.rental_payment is NOT NULL and rb.received_amount < rb.receivable_amount)
				)
			{condition}
		""".format(condition=conds))
	return data
	
def rbb_conditions(filters):
	conds = ""
	if filters.dzongkhag:
		conds += "and rb.dzongkhag='{}'".format(filters.get("dzongkhag"))
	if filters.location:
		conds += "and rb.location='{}'".format(filters.location)

	report_date = filters.get("fiscal_year") + "-" + filters.get("month") + "-" + "01"
	from_date = get_first_day(report_date)
	to_date   = get_last_day(report_date)

	if from_date and to_date:
		conds += " and rb.posting_date between '{0}' and '{1}'".format(from_date, to_date)
	return conds


def get_columns(filters):
	columns = [
		("Tenant CID") + ":Data:100",
		("Tenant Name") + ":Data:150",
		("Posting Date") + ":Date:150",
		("Actual Rent Amount") + ":Currency:100",
		("Rent Received") + ":Currency:100",
		("Pre-rent Received") + ":Currency:100",
		("Excess Amount Received") + ":Currency:100",
		("Balance Rent Amount (Due)") + ":Currency:120",
		("Discount Amount") + ":Currency:100",
		("Penalty Amount") + ":Currency:100",
		
		("TDS Amount") + ":Currency:100",
		("Rent Write-off") + ":Currency:100",
		("Total Amount Received") + ":Currency:120",
		("Rental Official")+ ":Data:100",
		("Ministry/Agency") + ":Link/Ministry and Agency:150",
		("Department") + ":Link/Tenant Department:150",
		("Branch") + "::150",
		("Fiscal Year") + ":Link/Fiscal Year:100",
		("Month") + ":Data:100",
		("Payment Mode") + "::150",
		("Credit Account") + ":Link/Account:150",
		("Tenant") + ":Link/Tenant Information:100",
		("Rental Bill") + ":Link/Rental Bill:150"
	]
	return columns

def get_data(filters):
	conds = conditions(filters)
	data = frappe.db.sql("""
			select 
				rpi.cid,
				rpi.tenant_name,
				rp.posting_date,
				rpi.bill_amount,
				rpi.rent_received,
				rpi.pre_rent_amount,
				rpi.excess_amount,
				rpi.balance_rent,
				rpi.discount_amount,
				rpi.penalty,
				
				rpi.tds_amount,
				rpi.rent_write_off_amount,
				rpi.total_amount_received,
				rp.rental_official_name,
				rp.ministry_agency,
				rpi.department,
				rp.branch,
				rpi.fiscal_year,
				rpi.month,
				rp.payment_mode,
				rp.credit_account,
				rpi.tenant,
				rpi.rental_bill
			from `tabRental Payment` rp, `tabRental Payment Item` rpi
			where rp.name = rpi.parent
			and rp.docstatus = 1
			{condition}
		""".format(condition=conds))
	return data


def conditions(filters):
	rb_conds = ""
	conds = ""
	report_date = filters.get("fiscal_year") + "-" + filters.get("month") + "-" + "01"
	from_date = get_first_day(report_date)
	to_date   = get_last_day(report_date)

	if filters.dzongkhag:
		rb_conds += """ and rb.dzongkhag = '{}' """.format(filters.dzongkhag)
	if filters.location:
		rb_conds += """ and rb.location='{}' """.format(filters.location)
	if filters.building_category:
		rb_conds += """ and rb.building_category='{}' """.format(filters.building_category)
	if rb_conds:
		conds += """ and exists(select 1
					from `tabRental Bill` rb
					where rb.docstatus = 1
					and rb.tenant = rpi.tenant
					{})""".format(rb_conds)
				
	if filters.rental_official: 
		conds += " and rp.rental_official_name = '{}'".format(filters.rental_official)

	if filters.ministry_agency:
		conds += """ and rpi.ministry_agency='{}' """.format(filters.ministry_agency)
	if filters.department:
		conds += """and rpi.department='{}'""".format(filters.department)
	
	if filters.get("payment_mode"):
		conds += " and rp.payment_mode = '{0}'".format(filters.get("payment_mode"))
	if from_date and to_date:
		conds += " and rp.posting_date between '{0}' and '{1}'".format(from_date, to_date)
	if filters.building_classification:
		conds += """ and exists( select 1 from `tabTenant Information` ti where ti.name = rpi.tenant 
					 and ti.building_classification = '{0}')""".format(filters.building_classification)
	return conds
