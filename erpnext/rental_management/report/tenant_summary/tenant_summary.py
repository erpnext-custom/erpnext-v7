# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
	("Month") + ":Data:90",
	("Fiscal Year") + ":Data:90",
	("Actual Rent Amount") + ":Currency:120",
	("Bill Amount") + ":Currency:120",
	("Rent Received") +":Currency:100",
	("Penalty") +":Currency:100",
	("Pre Rent Received") + " :Currency:120",
	("Excess Amount Received") + " :Currency:120",
	("Discount Amount") + " :Currency:120",
	("Security Deposit Amount") + " :Currency:120",
	("Balance Rent") + " :Currency:120",
	("Total Amount Received") + " :Currency:120",
	("Rental Bill No") + " :Link/Rental Bill:150",
	]


def get_data(filters):
	cond = ''
	if filters.get("name"):
		cond = " rb.tenant = \'" + str(filters.name) + "\'"

	query = """
		SELECT
			rb.month,
			rb.fiscal_year,
			rb.rent_amount,
			(rb.receivable_amount - rb.adjusted_amount - rb.discount_amount - rb.tds_amount - rb.penalty) as bill_amount,
			IfNull((Select rpi.rent_received From `tabRental Payment Item` rpi Where rpi.rental_bill = rb.name),''),
			IfNull((Select rpi.penalty From `tabRental Payment Item` rpi Where rpi.rental_bill = rb.name),''),
			IfNull((Select rpi.pre_rent_amount From `tabRental Payment Item` rpi Where rpi.rental_bill = rb.name),''),
			IfNull((Select rpi.excess_amount From `tabRental Payment Item` rpi Where rpi.rental_bill = rb.name),''),
			IfNull((Select rpi.discount_amount From `tabRental Payment Item` rpi Where rpi.rental_bill = rb.name),''),
			IfNull((Select rpi.sa_amount From `tabRental Payment Item` rpi Where rpi.rental_bill = rb.name),''),
			IfNull((Select rpi.balance_rent From `tabRental Payment Item` rpi Where rpi.rental_bill = rb.name),''),
			IfNull((Select rpi.total_amount_received From `tabRental Payment Item` rpi Where rpi.rental_bill = rb.name),''),
			rb.name
		FROM
			`tabRental Bill` as rb
		WHERE
			{condition}
			""".format(
				condition = cond
			)

	query += " ORDER BY rb.month, rb.fiscal_year"

	return frappe.db.sql(query)