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
		("Branch") + ":Link/Branch:120",
		("Customer") + ":Link/Customer:120",
		("Bill Name") + ":Link/Hire Charge Invoice:120",
		("Equipment")+ ":Data:120",
		("Equipment No.") + ":Data:120",
		("Work Rate") + ":Currency:100",
		("Idle Rate") +":Currency:100",
		("Private")+":Currency:100",
		("Others") +":Currency:100",
		("CDCL") +":Currency:100",
		("Amount") + ":Currency:150"
	]

def get_data(filters):

	query = ("""select hic.branch, hic.customer, hic.name, hid.equipment, hid.equipment_number, hid. work_rate, hid.idle_rate,
CASE hic.owned_by
	WHEN 'Private' THEN SUM(hid.total_amount)
	END as Private,
CASE hic.owned_by
	WHEN 'Others' THEN SUM(hid.total_amount)

	END AS Others,
CASE hic.owned_by
	WHEN 'CDCL' THEN 
	SUM(hid.total_amount)

END AS CDCL,
SUM(hid.total_amount) 
from `tabHire Charge Invoice` as hic, `tabHire Invoice Details` as hid, `tabEquipment` e
where hic.name = hid.parent and hid.equipment = e.name and hic.docstatus = 1 """)

	if filters.get("branch"):
		query += " and hic.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and hic.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	if filters.get("not_cdcl"):
                query += " and e.not_cdcl = 0"
	if filters.get("include_disabled"):
                query += " "
        else:
                query += " and e.is_disabled = 0"
	query += " group by hic.customer, hic.name, hid.equipment "
	return frappe.db.sql(query)


