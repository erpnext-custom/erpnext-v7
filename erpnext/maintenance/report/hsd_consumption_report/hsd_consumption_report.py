# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr

def execute(filters=None):
	columns = get_columns()
	query = construct_query(filters)
	data = get_data(query, filters = None)

	return columns, data, query
def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		row = [d.equipment_type, d.equipment_number, d.branch, d.min, d.max, d.distance,
		d.drawn,
		((flt(d.opening)+flt(d.drawn))*d.yardstickd),
		flt((d.drawn)+flt(d.opening+d.drawn)*d.yardstick),
		d.yardstick,
		flt(d.opening)+
		(flt(d.drawn)-(flt(d.opening)+flt(d.drawn))*d.yardstickd),
		d.opening,d.rate,
		((flt(d.drawn)-(flt(d.opening)+flt(d.drawn))*d.yardstickd))*d.rate]
		data.append(row);
	return data


def construct_query(filters):
	query = """select e.equipment_type as equipment_type, e.equipment_number as equipment_number,
	vl.branch branch, MIN(vl.initial_km) as min,
	MAX(vl.final_km) as max,
	SUM(distance_km) distance,
	case
	when cp.date> "str(filters.from_Date)"
	then SUM(cp.qty)
	else 0
	end as drawn

	CASE WHEN cp.date < "str(filters.from_date)"
	THEN sum(cp.qty)
	else 0
	END  AS opening,



	CASE
	WHEN hcp.lph
	THEN hcp.lph
	WHEN hcp.kph
	THEN hcp.kph
	END as yardstick,
	vl.work_rate as rate,
	FROM `tabConsumed POL` cp, `tabVehicle Logbook` vl,
	`tabEquipment` e, `tabHire Charge Parameter` hcp  where hcp.equipment_model = e.equipment_model and e.equipment_number = vl.equipment_number
	AND cp.equipment = vl.equipment
	AND cp.docstatus = '1'"""

	 #GROUP BY e.equipment_number

	if filters.get("branch"):
		query += " and vl.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and cp.date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	query += " GROUP BY e.equipment_number "
	return query

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
