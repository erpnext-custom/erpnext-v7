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

	return columns,data, query
def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		row = [d.ty, d.no, d.br, d.min, d.max, flt(d.max)-flt(d.min),
		d.drawn, d.opening, flt(d.drawn)+flt(d.opening),
		d.yardstick, d.consumed, d.closing, d.rate, flt(d.rate)*flt(d.consumed)]
		data.append(row);
	return data


def construct_query(filters):
	query = """select hcp.equipment_type ty,  e.equipment_number  as no, pol.branch br, MIN(vl.initial_km) AS min, MAX(vl.final_km) AS max, (select sum(vl.hsd_received) from `tabVehicle Logbook` vl) AS drawn,
	CASE
	WHEN vl.to_date < '%(from_date)s'
	then (select vl.opening_balance from `tabVehicle Logbook` vl where vl.equipment = pol.equipment order by vl.to_date asc limit 1)
	else 0
	end as opening,
	CASE
	WHEN hcp.lph
	THEN hcp.lph
	WHEN hcp.kph
	THEN hcp.kph
	END AS yardstick,
	(select sum(vl.consumption) from `tabVehicle Logbook` vl) as consumed,
	case
	when vl.to_date > '%(from_date)s'
	then (select vl.closing_balance from `tabVehicle Logbook` vl where vl.equipment = pol.equipment order by vl.to_date desc limit 1)
	else 0
	end as closing,
	avg(pol.rate) as rate from  `tabHire Charge Parameter` hcp, `tabEquipment` e, `tabVehicle Logbook` vl, `tabPOL` pol where hcp.equipment_model = e.equipment_model and  vl.equipment = pol.equipment and  e.equipment_number = vl.equipment_number and vl.docstatus = 1 """ % {"from_date": str(filters.from_date)}

	if filters.get("branch"):
		query += " and pol.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		query += " and pol.date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"
	query += " GROUP BY e.equipment_number "
	frappe.msgprint(query)
	return query

def get_columns():
	cols = [
		("Equipment Type.") + ":data:120",
		("Registration No") + ":data:120",
		("Location")+":data:120",
		("Initial KM/H Reading")+":data:100",
		("Final KM/H Reading")+":data:100",
		("KM/Hrs")+":data:100",
		("HSD Drawn(L)")+":data:100",
		("Previous Balance(L)")+":data:100",
		("Total HSD(L)")+":data:100",
		("Rate of Consumption")+":data:110",
		("HSD Consumption(L)")+":data:110",
		("Closing Balance(L)")+":data:110",
		("Rate(Nu.)")+":currency:100",
		("Amount(Nu.)")+":currency:100",

	]
	return cols
