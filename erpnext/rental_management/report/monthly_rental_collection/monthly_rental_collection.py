# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


###########Created by Cheten on 05/10/2020#################################
from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters=None):
	columns = [
		("Branch") + ":Link/Branch:150",
		("Posting Date") + ":Date:150",
		("Fiscal Year") + ":Data:100",
		("Month") + ":Data:100",
		("Payment Mode") + ":Data:150",
		("Ministry/Agency") + ":Data:150",
		("Credit Account") + ":Data:150",
		("Tenant") + ":Link/Tenant Information:100",
		("Tenant Name") + ":Data:150",
		("Rental Bill") + ":Data:150",
		("Actual Rent Amount") + ":Data:100",
		("Amount") + ":Data:100",
		("Amount Received") + ":Data:100",
		("Department") + ":Data:150"

	]
	return columns

def get_data(filters):
	data=frappe.db.sql(
		"""
			select 
				rp.branch
				,rp.posting_date
				,rp.fiscal_year
				,rp.month
				,rp.payment_mode
				,rp.ministry_agency
				,rp.credit_account
				,rpi.tenant
				,rpi.tenant_name
				,rpi.rental_bill
				,rpi.actual_rent_amount
				,rpi.amount
				,rpi.amount_received
				,rpi.department
			from `tabRental Payment` rp, `tabRental Payment Item` rpi
			where rp.docstatus = 1 and rp.name=rpi.parent and posting_date between '{from_date}' and '{to_date}'
		""".format(from_date=filters.from_date,to_date=filters.to_date)
	)
	return data





