# For license information, please see license.txt
# Frappe Technologiss Pvt. Ltd. and contributors

# Created by Phuntsho on August 17 2020

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
	("Tenant Code") + ":Data:120",
	("CID No.") + ":Data:120",
	("Tenant Name") + ":Data:120",
	("Fiscal Year") + ":Data:80",
	("Month") + " :Data:80",
	("Actual Rent Amount") + ":Currency:120",
	("Bill Amount") + ":Currency:120",
	("Amount Received") + ":Currency:120",
	("Balance Amount") + ":Currency:120",
	("Department") + ":Data:100",
	("Block No.") + ":Data:120",
	("Flat No. ") + ":Data:120",
	# ("Building Classification") + ":Data:120",
	("Ministry/Agency.") + ":Data:120",
	("Payment Mode") + ":Data:90",
	("Rental Official Name") + ":Data:90",
	("Bill No") + ":Link/Rental Bill:130",
	("Penalty")+ ":Currency:120",
	("Dzongkhag") +":Data:100",
	("Location")+":Data:100",
	("Town Category") +":Data:100",
	("Building Category") +":Data:100",
	]

def get_data(filters):
	status = ""
	if filters.get("status") == "Draft":
		status = "and rb.docstatus = 0"
	if filters.get("status") == "Submitted":
		status = "and rb.docstatus = 1"

	query = """
		SELECT
			rb.tenant,
			rb.cid,
			rb.tenant_name,
			rb.fiscal_year,
			rb.month,
			rb.rent_amount,
			rpi.amount,
			rpi.amount_received,
			(rpi.amount-rpi.amount_received) as balance,
			rb.department,
			rb.block_no,
			rb.flat_no,
			rb.ministry_agency,
			rpi_parent.payment_mode,
			rpi_parent.rental_official_name,
			rb.name,
			IF (rb.rental_payment != ' ',
				(IF
					(rb.received_amount <= 0,
						0,
						rpi.penalty
					)
				),
				0
			),
			rb.dzongkhag,
			rb.location,
			rb.town_category,
			rb.building_category
		FROM
			`tabRental Bill` as rb, 
			`tabRental Payment Item` as rpi,
			`tabRental Payment` as rpi_parent
		WHERE
			rb.name = rpi.rental_bill AND 
			rpi.docstatus = 1 AND	
			rpi.parent = rpi_parent.name AND 
			rpi_parent.docstatus = 1
			{status}
			""".format(
				status = status
			)
	if filters.get("dzongkhag"):
		query += " and rb.dzongkhag = \'" + str(filters.dzongkhag) + "\'"
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
	
	# if filters.get("month"):
	# 	query += " and rb.month = {0}".format(filters.get("month"))

	if filters.get("fiscal_year"):
		query += " and rb.fiscal_year ={0}".format(filters.get("fiscal_year"))

	if filters.get("payment_mode") and filters.get("payment_mode") != "":
		query += " and rpi_parent.payment_mode = '{0}'".format(filters.get("payment_mode"))

	if filters.get("rental_official"):
		if filters.get("rental_official") == 'Dorji Wangmo': 
			# two dorji wangmo in the system. use the below
			official = "NHDCL1905030"
		else: 
			emp = frappe.db.sql("select name from tabEmployee where employee_name = '{}'".format(filters.get("rental_official")), as_dict=True)
			official = emp[0].name
		query += " and rpi_parent.rental_official = '{0}'".format(official)

	if filters.get("from_month") == filters.get("to_month"): 
		query += " and rb.month = {0}".format(filters.get("from_month"))

	if filters.get("from_month") != filters.get("to_month"): 
		query += " and rb.month between {0} and {1}".format(filters.get("from_month"),filters.get("to_month"))
	
	

	# # Cannot look at a month by itself.
	# if filters.get("from_month") and filters.get("to_month"):
	# 	query += " and rb.month between {0} and {1}".format(filters.get("from_month"),filters.get("to_month"))

	return frappe.db.sql(query)


