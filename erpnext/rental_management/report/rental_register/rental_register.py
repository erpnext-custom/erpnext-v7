# For license information, please see license.txt
# Frappe Technologiss Pvt. Ltd. and contributors

# Created by Phuntsho on August 17 2020

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
def execute(filters=None):
	columns = get_columns()
	queries = construct_query(filters);
	data = get_data(queries)
	return columns, data

def get_columns():
	return [
	("Tenant Code") + ":Data:120",
	("Tenant Name") + ":Data:120",
	("CID No.") + ":Data:120",
	("Dzongkhag") +":Data:100",
	("Dungkhag") +":Data:90",
	("Month") + " :Data:80",
	("Posting Date") + " :Date:80",
	("Fiscal Year") + ":Data:80",
	("Actual Rent Amount") + ":Currency:120",
	("Adjusted Amount") + ":Currency:100",
	("Bill Amount") + ":Currency:120",
	("Amount Received") + ":Currency:120",
	("Pre-rent Received") + ":Currency:120",
	("Excess Amount Received") + ":Currency:120",
	("Balance Rent Amount (Due)") + ":Currency:120",
	("Discount Amount") + ":Currency:120",
	("Late Payment Penalty") + ":Currency:120",
	("TDS  Deducted") + ":Currency:120",
	("Rent Write-off") + ":Currency:120",
	("Total Amount Received") + ":Currency:120",
	("Rental Income") + ":Currency:120",
	("Rental Bill ID") + ":Link/Rental Bill:130",
	("Payment ID") + ":Data:120",
	("Status") + ":Data:90",

	("Location")+":Data:100",
	("Building Category") +":Data:100",
	("Department") + ":Data:100",
	("Block No.") + ":Data:120",
	("Flat No. ") + ":Data:120",
	# ("Building Classification") + ":Data:120",
	("Ministry/Agency.") + ":Data:120",
	("Payment Mode") + ":Data:90",
	("Rental Official Name") + ":Data:90",
	# ("Bill No") + ":Link/Rental Bill:130",
	# ("Penalty")+ ":Currency:120",
	("Town Category") +":Data:100",
	]

def get_data(query):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	rental_name = []
	for d in datas:
		credit = 0
		if d.building_category in ('Residential','Commercial','Changjiji Vegetable Market','Special Housing') and d.rental_bill not in rental_name:
			rental_name.append(d.rental_bill)

			for a in frappe.db.sql(""" Select credit From `tabGL Entry` where account =
							(
								select i.account from `tabRental Account Setting Item` i
									Where i.building_category = '{}'
							) 
							and voucher_no = '{}' """.format(d.building_category, d.rental_bill), as_dict=True):
				
				credit = a.credit
		if not credit:
			credit = 0

		row = [d.tenant, d.tenant_name, d.cid, d.dzongkhag, d.dungkhag, d.month, d.posting_date, d.fiscal_year, d.rent_amount, d.adjusted_amount, d.bill_amount,
				d.rent_received, d.pre_rent_amount, d.excess_amount, d.balance_rent, d.discount_amount, d.penalty, d.tds_amount, d.rent_write_off, d.total_amount_received, 
				credit, d.rental_bill, d.rental_payment, d.docstatus, d.location, d.building_category, d.department, d.block_no, d.flat_no, d.ministry_agency, d.payment_mode,
				d.rental_official_name, d.town_category]
		data.append(row)

	return data
			
def construct_query(filters):

	status = ""
	if filters.get("status") == "Draft":
		status = "rb.docstatus = 0"
	if filters.get("status") == "Submitted":
		status = "rb.docstatus = 1"

	# payment_due_on = frappe.db.get_single_value("Rental Setting","payment_due_on")
	# penalty_rate = float(frappe.db.get_single_value("Rental Setting","penalty_rate"))/100.0

	
			# CASE 
			# 	WHEN rb.building_category IN ('Residential','Commercial','Changjiji Vegetable Market','Special Housing')
			# 		THEN
			# 			(Select credit From `tabGL Entry` where account =
			# 				(
			# 					select i.account from `tabRental Account Setting Item` i
			# 						Where i.building_category = rb.building_category
			# 				) 
			# 				and voucher_no = rb.name )
			# 	ELSE 0
			# END AS rent_income,
			
	query = """
		SELECT
			rb.tenant tenant,
			rb.tenant_name tenant_name,
			rb.cid cid,
			rb.dzongkhag dzongkhag,
			rb.dungkhag dungkhag,
			rb.month month,
			rpi_parent.posting_date posting_date,
			rb.fiscal_year fiscal_year,
			rb.rent_amount rent_amount,
			rb.adjusted_amount adjusted_amount,
			(rb.receivable_amount - rb.adjusted_amount - rb.discount_amount - rb.tds_amount - rb.penalty) as bill_amount,
			rpi.rent_received rent_received,
			rpi.pre_rent_amount pre_rent_amount,
			rpi.excess_amount excess_amount,
			rpi.balance_rent balance_rent,
			rpi.discount_amount discount_amount,
			rpi.penalty penalty,
			rpi.tds_amount tds_amount,
			rpi.rent_write_off_amount rent_write_off,
			rpi.total_amount_received total_amount_received,
			
			rb.name as rental_bill,
			rpi_parent.name rental_payment,

			CASE rpi_parent.docstatus
				WHEN '1'
					THEN 'Submitted'
				WHEN '2'
					THEN 'Cancelled'
				WHEN '0'
					THEN 'Draft'
				ELSE ''
			END as docstatus,

			rb.location location,
			rb.building_category building_category,
			rb.department department,
			rb.block_no block_no,
			rb.flat_no flat_no,
			rb.ministry_agency ministry_agency,
			rpi_parent.payment_mode payment_mode,
			rpi_parent.rental_official_name rental_official_name,
			rb.town_category town_category
		FROM
			`tabRental Bill` as rb
		LEFT JOIN
			`tabRental Payment Item` as rpi
		ON
			rb.name = rpi.rental_bill AND rpi.docstatus = 1
		LEFT JOIN
			`tabRental Payment` as rpi_parent
		ON
			rpi.parent = rpi_parent.name AND rpi_parent.docstatus = 1
		WHERE
			{status}
			""".format(
				status = status
			)

	if filters.get("dzongkhag"):
		query += " and rb.dzongkhag = \'" + str(filters.dzongkhag) + "\'"

	if filters.get("dungkhag"):
		query += " and rb.dungkhag = \'" + str(filters.dungkhag) + "\'"

	if filters.get("location"):
		query += " and rb.location = \'" + str(filters.location) + "\' "

	if filters.get("town"):
		query += " and rb.town_category = \'" + str(filters.town) + "\' "

	if filters.get("ministry"):
		query += " and rb.ministry_agency = \'" + str(filters.ministry) + "\' "

	if filters.get("department"):
		query += " and rb.department = \'" + str(filters.department) + "\' "
		
	if filters.get("building_category"):
		query += " and rb.building_category = \'" + str(filters.building_category) + "\' "
	if filters.get("month"):
		query += " and rb.month = {0}".format(filters.get("month"))
	if filters.get("fiscal_year"):
		query += " and rb.fiscal_year ={0}".format(filters.get("fiscal_year"))
	if filters.get("payment_mode"):
		query += " and rpi_parent.payment_mode = '{0}'".format(filters.get("payment_mode"))

	if filters.get("rental_official"):
		if filters.get("rental_official") == 'Dorji Wangmo': 
			# two dorji wangmo in the system. use the below
			official = "NHDCL1905030"
		else: 
			emp = frappe.db.sql("select name from tabEmployee where employee_name = '{}'".format(filters.get("rental_official")), as_dict=True)
			official = emp[0].name
		query += " and rpi_parent.rental_official = '{0}'".format(official)

	if filters.get("building_classification"):
		query += " and building_classification = '{0}'".format(filters.get("building_classification"))
		
	if filters.get("from_month") and filters.get("to_month"):
		query += " and rb.month between {0} and {1}".format(filters.get("from_month"),filters.get("to_month"))
	query += " ORDER BY rb.tenant, rb.month"
	# return frappe.db.sql(query)
	return query
