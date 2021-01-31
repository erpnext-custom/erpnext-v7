# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

#############Created by Cheten Tshering on 26/10/2020#########################
from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	columns=[
		("Customer") + ":Link/Customer:100",
		("Branch") + ":Link/Branch:100",
		("Posting Date") + ":Date:100",
		("Reference Number") + "::150",
		("Item") + ":Link/Item:100",
		("Material Name") + "::100",
		("Quantity") + "::100",
		("UOM") + ":Link/UOM:100",
		("Rate") + ":Currency:100",
		("Amount") + ":Currency:100",
		("Total") + ":Currency:100",
		("Status") + "::100",
		("Remarks") + "::100"
	]

	return columns

def get_data(filters):
	conds = get_conditions(filters)
	data = frappe.db.sql(
		"""
		select 
			cpo.customer
			,cpo.branch
			,cpo.posting_date
			,cpo.reference_number
			,cpti.item
			,cpti.material_name
			,cpti.quantity
			,cpti.uom
			,cpti.rate
			,cpti.amount
			,cpo.total
			,cpo.status
			,cpo.remarks
		from `tabCustomer Pending Orders` cpo, `tabCustomer Pending Table Item` cpti
		where cpo.docstatus = 1 and cpo.name=cpti.parent and posting_date between '{start_date}' and '{to_date}'
		{condition}
		""".format(start_date=filters.start_date, to_date=filters.to_date, condition=conds)
	)
	return data

def get_conditions(filters):
	conds = ""
	if filters.customer:
		conds += "and customer='{}'".format(filters.customer)
	
	if filters.get("status") == "Pending":
		conds = "and status = 'Pending'"
	else:
		conds = "and status = 'Delivered'"
	return conds
