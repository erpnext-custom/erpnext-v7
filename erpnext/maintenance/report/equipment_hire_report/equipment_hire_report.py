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
		("Equipment") + ":Link/Equipment:120",
		("Equipment Type") + ":data:120",
		("Equipment No")+":data:100",
		("Hire Form Name")+":Link/Equipment Hiring Form:150",
		("Customer Name") + ":data:120",
		("Customer Type") + ":data:120",
		("Hour W Fuel")+":data:80",
		("Rate W Fuel")+":Currency:150",
		("Amount W Fuel")+":Currency:150",
		("Hour W/O Fuel")+":data:80",
		("Rate W/O Fuel")+":Currency:150",
		("Amount W/O Fuel")+":Currency:150",
		("Hour Cft-Broadleaf")+":data:80",
		("Rate Cft-Broadleaf")+":Currency:150",
		("Amount Cft-Broadleaf")+":Currency:150",
		("Hour Cft-Conifer")+":data:80",
		("Rate Cft-Conifer")+":Currency:150",
		("Amount Cft-Conifer")+":Currency:150",
		("Idle Hour")+ ":data:80",
       		("Idle Rate")+":Currency:150",
		("Idle Amount") + ":Currency:150",
		("Own Company")+":Currency:150",
		("Private")+":Currency:150",
		("Others")+":Currency:150",
		("Total Hire Charge")+":Currency:150",
	]

def get_data(filters):
	query ="""select hid.equipment, (select e.equipment_type FROM tabEquipment e WHERE e.name = hid.equipment), hid.equipment_number, hci.ehf_name, hci.customer, (select c.customer_group FROM tabCustomer AS c WHERE hci.customer = c.name),
        CASE hid.rate_type
        WHEN 'With Fuel' THEN (select sum(hid.total_work_hours))
        END,
        CASE hid.rate_type
        WHEN 'With Fuel' THEN (select hid.work_rate)
        END,
        CASE hid.rate_type
        WHEN 'With Fuel' THEN (select sum(hid.amount_work))
        END,
        CASE hid.rate_type
        WHEN 'Without Fuel' THEN (select sum(hid.total_work_hours))
        END,
        CASE hid.rate_type
        WHEN 'Without Fuel' THEN (select hid.work_rate)
        END,
        CASE hid.rate_type
        WHEN 'Without Fuel' THEN (select sum(hid.amount_work))
        END,
        CASE hid.rate_type
        WHEN 'Cft - Broadleaf' THEN (select sum(hid.total_work_hours))
        END,
        CASE hid.rate_type
        WHEN 'Cft - Broadleaf' THEN (select hid.work_rate)
        END,
        CASE hid.rate_type
        WHEN 'Cft - Broadleaf' THEN (select sum(hid.amount_work))
        END,
        CASE hid.rate_type
        WHEN 'Cft - Conifer' THEN (select sum(hid.total_work_hours))
        END,
        CASE hid.rate_type
        WHEN 'Cft - Conifer' THEN (select hid.work_rate)
        END,
        CASE hid.rate_type
        WHEN 'Cft - Conifer' THEN (select sum(hid.amount_work))
        END,
        sum(hid.total_idle_hours), hid.idle_rate, sum(hid.amount_idle),
        CASE hci.owned_by
        WHEN 'Own Company' THEN (select sum(hid.total_amount))
        END,
        CASE hci.owned_by
        WHEN 'Private' THEN (select sum(hid.total_amount))
        END,
        CASE hci.owned_by
        WHEN 'Others' THEN (select sum(hid.total_amount))
        END,sum(hid.total_amount) FROM `tabHire Invoice Details` AS hid, `tabHire Charge Invoice` AS hci, `tabEquipment` e,  
	`tabEquipment History` eh,`tabVehicle Logbook` vl   WHERE hid.parent = hci.name AND hid.vehicle_logbook = vl.name and hid.equipment = e.name  and e.name = eh.parent and eh.branch = hci.branch and hci.docstatus = 1 and ((vl.from_date between '{0}' and '{1}') or (vl.to_date between '{0}' and '{1}'))""".format(filters.get("from_date"), filters.get("to_date"))

	if filters.get("branch"):
		query += " and hci.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += """ and (('{0}' between eh.from_date and ifnull(eh.to_date, now())) or
		('{1}' between eh.from_date and ifnull(eh.to_date, now())))""".format(filters.get("from_date"), filters.get("to_date"))
	if filters.get("not_cdcl"):
		query += " and e.not_cdcl = 0"

	if filters.get("include_disabled"):
		query += " "
	else:
		query += " and e.is_disabled = 0"

	if filters.get("customer"):
		query += " and hci.customer = \'" + str(filters.customer) + "\'"
	query += " group by hid.equipment, hci.ehf_name"
	frappe.msgprint(query)
	return frappe.db.sql(query)
