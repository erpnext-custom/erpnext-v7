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
		("Job No.") + ":Link/Job Card:120",
		("Description") + ":data:300",
		("Equipment No")+":data:150",
		("Amount")+":Currency:150",
		("Customer")+":data:150"

	]

def get_data(filters):
	query ="""select jc.name, (select group_concat(jci.job_name separator ',') from `tabJob Card Item` jci where jci.parent = jc.name) as description, jc.equipment_number, jc.total_amount, jc.customer FROM `tabJob Card` AS jc, `tabBreak Down Report` AS bdr WHERE bdr.name = jc.break_down_report AND jc.docstatus = '1'"""
	if filters.get("branch"):
		query += " and jc.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and jc.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	if filters.get("customer"):
		query += " and jc.owned_by = \'" + str(filters.customer) + "\'"

	if filters.get("equipment"):
		query += " and jc.equipment_number = \'" + str(frappe.db.get_value("Equipment", filters.equipment, "equipment_number")) + "\'"
	return frappe.db.sql(query)
