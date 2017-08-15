# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns =get_columns()
	data =get_data(filters)
	return columns, data
def get_columns():
	return [
		("Equipment Type") + ":data:120",
		("Equipment No")+":data:100",
		("Equipment name")+":Link/Equipment Hiring Form:150",
		("Hour with Fuel")+":data:100",
		("Rate with Fuel")+":data:100",
		("Hour without Fuel")+":data:100",
		("Rate without Fuel")+":data:110",
		("Amount with Fuel")+":data:100",
		("Amount without Fuel")+":data:100",
		("Idle Hour")+ ":data:100",
        ("Idle Work Rate")+":data:100",
		("Idle Amount") + ":data:100",
		("Total Hire Charge")+":data:100"
	]

def get_data(filters):

	query = """select e.equipment_type, hid.equipment_number, ehf.name, hid.total_work_hours, hid.work_rate, hid.amount_work,hid.total_work_hours, hid.work_rate, hid.amount_work, hid.total_idle_hours, hid.idle_rate, hid.amount_idle, hid.total_amount FROM  tabEquipment AS e, `tabHire Invoice Details` AS hid, `tabHire Charge Invoice` AS hci,`tabEquipment Hiring Form` AS ehf WHERE hid.parent = hci.name AND hci.ehf_name = ehf.name AND e.equipment_hire_form =ehf.name AND ehf.docstatus = 1"""
	if filters.get("branch"):
		query += " and ehf.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and hci.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	if filters.get("customer"):
		query += " and hci.customer = \'" + str(filters.customer) + "\'"
	return frappe.db.sql(query)
