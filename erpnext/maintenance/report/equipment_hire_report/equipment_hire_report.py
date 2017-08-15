# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

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
		("Amount with Fuel")+":data:150",
		("Idle Hour With Fuel")+ ":data:150",
        ("Idle Work Rate with Fuel")+":data:170",
		("Idle Amount with fuel") + ":data:170",
		("Hour without Fuel")+":data:150",
		("Rate without Fuel")+":data:150",
		("Amount without Fuel")+":data:150",
		("Idle Hour without Fuel")+ ":data:170",
        ("Idle Work Rate without Fuel")+":data:180",
		("Idle Amount without fuel") + ":data:170",
		("Total Hire Charge")+":data:130"
	]

def get_data(filters):
	query ="""select (select equipment_type from tabEquipment a where a.name = hid.equipment) as equipemds, e.equipment_type, hid.equipment_number, ehf.name,
	CASE had.rate_type
	WHEN 'With Fuel' THEN (select hid.total_work_hours)
	END,
	CASE had.rate_type
	WHEN 'With Fuel' THEN (select hid.work_rate)
	END,
	CASE had.rate_type
	WHEN 'With Fuel' THEN (select hid.amount_work)
	END,
	CASE had.rate_type
	WHEN 'With Fuel' THEN(select hid.total_idle_hours)
	END,
	CASE had.rate_type
	WHEN 'With Fuel' THEN(select hid.idle_rate)
	END,
	CASE had.rate_type
	WHEN 'With Fuel' THEN(select hid.amount_idle)
	END,
	CASE had.rate_type
	WHEN 'Without Fuel' THEN (select hid.total_work_hours)
	END,
	CASE had.rate_type
	WHEN 'Without Fuel' THEN (select hid.work_rate)
	END,
	CASE had.rate_type
	WHEN 'Without Fuel' THEN (select hid.amount_work)
	END,
	CASE had.rate_type
	WHEN 'Without Fuel' THEN(select hid.total_idle_hours)
	END,
	CASE had.rate_type
	WHEN 'Without Fuel' THEN(select hid.idle_rate)
	END,
	CASE had.rate_type
	WHEN 'Without Fuel' THEN(select hid.amount_idle)
	END, hid.total_amount FROM  tabEquipment AS e, `tabHire Invoice Details` AS hid, `tabHire Charge Invoice` AS hci,`tabEquipment Hiring Form` AS ehf,`tabHiring Approval Details` as had WHERE hid.parent = hci.name AND hci.ehf_name = ehf.name AND e.equipment_hire_form =ehf.name AND had.parent = ehf.name AND ehf.docstatus = 1"""

	if filters.get("branch"):
		query += " and ehf.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and hci.posting_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	if filters.get("customer"):
		query += " and hci.customer = \'" + str(filters.customer) + "\'"
	return frappe.db.sql(query)
