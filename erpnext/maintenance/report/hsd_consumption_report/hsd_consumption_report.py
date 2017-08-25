# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():
	cols = [
		("Equipment Type.") + ":data:150",
		("Registration No") + ":data:150",
		("Location")+":data:150",
		("Initial KM/H Reading")+":data:150",
		("Final KM/H Reading")+":data:150",
		("KM/H")+":data:150",
		("HSD Drawn(L)")+":data:150",
		("Previous Balance(L)")+":data:150",
		("Total HSD(L)")+":data:150",
		("Rate of Consumption")+":data:150",
		("HSD Consumption(L)")+":data:150",
		("Opening Balance(L)")+":data:150",
		("Rate(Nu.)")+":currency:150",
		("Amount(Nu.)")+":currency:150",
		
	]
	return cols

def get_data(filters):
	data = """select e.equipment_type, e.equipment_number, vl.branch, MIN(vl.initial_km),
	MAX(vl.final_km),SUM(distance_km), SUM(cp.qty)  AS drawn,
	CASE WHEN cp.date < "str(filters.from_date)"
	THEN sum(cp.qty)
	END  AS opening,
	SUM(cp.qty) as total,
	CASE
	WHEN hcp.lph
	THEN hcp.lph
	WHEN hcp.kph
	THEN hcp.kph
	END as yardstick,
	SUM(cp.qty+cp.qty-cp.qty) AS consumed,
	CASE
	WHEN hcp.lph
	THEN SUM((cp.qty+cp.qty)*hcp.lph)
	WHEN hcp.kph
	THEN sum((cp.qty+cp.qty)/hcp.kph)
	end as closing, vl.work_rate, SUM(vl.work_rate*cp.qty)
	FROM `tabConsumed POL` cp, `tabVehicle Logbook` vl,
	`tabEquipment` e, `tabHire Charge Parameter` hcp  where hcp.equipment_model = e.equipment_model and e.equipment_number = vl.equipment_number
	AND cp.equipment = vl.equipment
	AND cp.docstatus = '1'"""

	 #GROUP BY e.equipment_number

	if filters.get("branch"):
		data += " and vl.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		data += " and cp.date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	data += " GROUP BY e.equipment_number "
	return frappe.db.sql(data)
