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
		("Equipment ") + ":Link/Equipment:120",
		("Equipment No.") + ":Data:120",
		("Operator")+ ":Data:100",
		("POL Type") + ":Data:120",
		("UoM") + ":Data:120",
		("Quantity") + ":Data:120"
	]

def get_data(filters):

	query =  "select e.name, e.equipment_number, e.current_operator, p.pol_type, (select uom from `tabPOL Type` pt where pt.name = p.pol_type) as uom,sum(p.qty) FROM tabEquipment AS e, `tabConsumed POL` AS p WHERE e.name = p.equipment"

	if filters.get("branch"):

		query += " and p.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):

		query += " and p.date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	
	if filters.get("not_cdcl"):
                query += " and e.not_cdcl = 0"

	if filters.get("include_disabled"):
                query += " "
        else:
                query += " and e.is_disabled = 0"

	query += " group by e.name, p.pol_type"

	return frappe.db.sql(query)
