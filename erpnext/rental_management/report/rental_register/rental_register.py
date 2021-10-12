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
<<<<<<< HEAD
		("Tenant Code. ") + ":Link/Tenant Bill:120",
		("CID No.") + ":Data:120",
        ("Tenant Name") + ":Data:120",
        ("Ministry/Agency.") + ":Data:120",
        ("Department") + ":Data:100",
        ("Block No.") + ":Data:120",
        ("Flat No. ") + ":Data:120",
        ("Rent Amount") + ":Currency:120",
        ("Paid Amount") + ":Currency:120",
		("Balance Amount") + ":Currency:120",
		("Payment Mode") + ":Data:90",
		("Rental Official Name") + ":Data:90",
	    ("Bill No") + ":Link/Rental Bill:130",
        ("Penalty")+ ":Currency:120",
        ("Dzongkhag") +":Data:100",
        ("Location")+":Data:100",
        ("Town Category") +":Data:100",
        ("Building Category") +":Data:100",
        ("Classification") + ":Data:150",
        ("Fiscal Year") + ":Data:80",
        ("Month") + " :Data:80",        
	]

def get_data(filters):
	
	status = ""
	if filters.get("status") == "Draft":
		status = "rb.docstatus = 0 and rb.docstatus != 2"
	if filters.get("status") == "Submitted":
		status = "rb.docstatus = 1 and rb.docstatus != 2"	

	payment_due_on = frappe.db.get_single_value("Rental Setting","payment_due_on")
	penalty_rate = float(frappe.db.get_single_value("Rental Setting","penalty_rate"))/100.0

	query = """
		SELECT 
			rb.tenant,  
			rb.cid,
			rb.tenant_name, 
			rb.ministry_agency, 
			rb.department, 
			rb.block_no, 
			rb.flat_no, 
			rb.rent_amount, 
			rb.received_amount, 
			(rb.received_amount - rb.rent_amount) as balance,
			rpi_parent.payment_mode,
			rpi_parent.rental_official_name,
			rb.name,
			IF (rb.rental_payment != ' ', 
				(IF (rb.received_amount <= 0, 
					"", 
					rpi.penalty)
				),
				( IF 
					(rb.posting_date < CURDATE() - {due_on},
						(
							( (SELECT TIMESTAMPDIFF(MONTH, rb.posting_date, CURDATE()))+1 )* (
								{pen_rate} *rb.rent_amount)
						),
						0
					)
				)
			),
			rb.dzongkhag, 
			rb.location, 
			rb.town_category, 
			rb.building_category,
			'class', 
			rb.fiscal_year, 
			rb.month
			
		FROM 
			`tabRental Bill` as rb

		LEFT JOIN 
			`tabRental Payment Item` as rpi
		ON
			rb.name = rpi.rental_bill AND rpi.docstatus != 2
			
		LEFT JOIN
			`tabRental Payment` as rpi_parent 
		ON 
			rpi.parent = rpi_parent.name
		WHERE 
			{status}
			""".format(
				status = status, 
				due_on = payment_due_on, 
				pen_rate = penalty_rate,
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
=======
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
	("Total Amount Received") + ":Currency:120",
	# ("Rental Income") + ":Currency:120",
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

def get_data(filters):

	status = ""
	if filters.get("status") == "Draft":
		status = "rb.docstatus = 0"
	if filters.get("status") == "Submitted":
		status = "rb.docstatus = 1"

	# payment_due_on = frappe.db.get_single_value("Rental Setting","payment_due_on")
	# penalty_rate = float(frappe.db.get_single_value("Rental Setting","penalty_rate"))/100.0

	query = """
		SELECT
			rb.tenant,
			rb.tenant_name,
			rb.cid,
			rb.dzongkhag,
			rb.dungkhag,
			rb.month,
			rpi_parent.posting_date,
			rb.fiscal_year,
			rb.rent_amount,
			rb.adjusted_amount,
			(rb.receivable_amount - rb.adjusted_amount - rb.discount_amount - rb.tds_amount - rb.penalty) as bill_amount,
			rpi.rent_received,
			rpi.pre_rent_amount,
			rpi.excess_amount,
			rpi.balance_rent,
			rpi.discount_amount,
			rpi.penalty,
			rpi.tds_amount,
			rpi.total_amount_received,
			
			rb.name,
			rpi_parent.name,

			CASE rpi_parent.docstatus
				WHEN '1'
					THEN 'Submitted'
				WHEN '2'
					THEN 'Cancelled'
				WHEN '0'
					THEN 'Draft'
				ELSE ''
			END as docstatus,

			rb.location,
			rb.building_category,
			rb.department,
			rb.block_no,
			rb.flat_no,
			rb.ministry_agency,
			rpi_parent.payment_mode,
			rpi_parent.rental_official_name,
			rb.town_category
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
		
>>>>>>> 97f6844854861dd57d6c2c035de8074716298c09
	if filters.get("building_category"):
		query += " and rb.building_category = \'" + str(filters.building_category) + "\' "
	if filters.get("month"):
		query += " and rb.month = {0}".format(filters.get("month"))
	if filters.get("fiscal_year"):
		query += " and rb.fiscal_year ={0}".format(filters.get("fiscal_year"))
<<<<<<< HEAD
	if filters.get("payment_mode"): 
		query += " and rpi_parent.payment_mode = '{0}'".format(filters.get("payment_mode"))
	if filters.get("rental_official"): 
		query += " and rpi_parent.rental_official = '{0}'".format(filters.get("rental_official"))
	
	return frappe.db.sql (query)
=======
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
	return frappe.db.sql(query)
>>>>>>> 97f6844854861dd57d6c2c035de8074716298c09
