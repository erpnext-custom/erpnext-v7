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
		("Customer") + ":Link/Customer:120",
		("Bill Name") + ":Data:120",
		("Equipment")+ ":Data:120",
		("Equipment No.") + ":Data:120",
		("Work Rate") + ":Data:100",
		("Idle Rate") +":Data:100",
		("Private")+":Data:100",
		("Others") +":Data:100",
		("CDCL") +":Data:100",
		("Amount") + ":Data:100"
	]

def get_data(filters):

	query = ("""select hic.customer, hic.name, hid.equipment, hid.equipment_number, hid. work_rate, hid.idle_rate,
CASE hic.owned_by
	WHEN 'Private' THEN hic.total_invoice_amount
	END as Private,
CASE hic.owned_by
	WHEN 'Others' THEN hic.total_invoice_amount
	END AS Others,
CASE hic.owned_by
	WHEN 'CDCL' THEN hic.total_invoice_amount
	END AS CDCL,
hic.total_invoice_amount
from `tabHire Charge Invoice` as hic, `tabHire Invoice Details` as hid
where hic.name = hid.parent """)

	if filters.get("branch"):
		query += " and hic.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and hic.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	query += " order by hic.customer "
	return frappe.db.sql(query)
