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

	return columns,data
def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		row = [d.ty, d.no, d.br, (d.mink, d.minh), (d.maxk,d.maxh), round(d.maxk-d.mink,2), round(d.maxh-d.minh,2),
		round(flt(d.drawn),2), round(flt(d.opening),2), round((flt(d.drawn)+flt(d.opening)),2),
		d.yskm, d.yshour, round(d.consumed,2), round(flt(d.closing),2), flt(d.cap), round(flt(d.rate),2), round((flt(d.rate)*flt(d.consumed)),2)]
		data.append(row);
	return data
	#KM and Hour value is changed from consumption_km and consumption_hours to diference between the final and initial after discussing with Project Lead
def construct_query(filters):
	query = """select e.equipment_type ty, e.equipment_number as no, e.branch br, MIN(vl.initial_km)  AS mink, MAX(vl.final_km) AS maxk, MIN(vl.initial_hour) as minh, MAX(vl.final_hour) as maxh, vl.consumption_km as ckm, vl.consumption_hours as ch,
	(select (sum(pol.qty*pol.rate)/sum(pol.qty)) from tabPOL pol where pol.branch = e.branch and pol.docstatus = 1) as rate,
	sum(vl.hsd_received) as drawn,
	(select a.opening_balance from `tabVehicle Logbook` a where a.rate_type = 'With Fuel' and a.equipment_number = e.equipment_number and a.from_date between \'%(from_date)s\' and \'%(to_date)s\' and a.to_date between \'%(from_date)s\' and \'%(to_date)s\' order by a.from_date asc limit 1) as opening, (select em.tank_capacity from  `tabEquipment Model` em where em.model = e.equipment_model) as cap,
	CASE
	WHEN vl.ys_km THEN vl.ys_km
	else 0
	end as yskm,
	CASE
	WHEN vl.ys_hours THEN vl.ys_hours
	else 0
	end as yshour,
	sum(vl.distance_km) as km,
	sum(vl.consumption) as consumed,
	(select a.closing_balance from `tabVehicle Logbook` a where a.rate_type = 'With Fuel' and a.equipment_number = e.equipment_number and a.from_date between \'%(from_date)s\' and \'%(to_date)s\' and a.to_date between \'%(from_date)s\' and \'%(to_date)s\' order by a.from_date desc limit 1) as closing  
	from `tabEquipment` e, `tabVehicle Logbook` vl where e.equipment_number = vl.equipment_number
	and vl.docstatus = 1"""  %{"from_date": str(filters.from_date), "to_date": str(filters.to_date),"branch": str(filters.branch)}

	if filters.get("branch"):
		query += " and e.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		 query += " and vl.from_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\' and vl.to_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

	if filters.get("not_cdcl"):
               query += " and e.not_cdcl = 0"
	if filters.get("include_disabled"):
                query += " "
        else:
                query += " and e.is_disabled = 0"

	query += " GROUP BY e.equipment_number "
	return query

def get_columns():
	cols = [
		("Equipment Type.") + ":data:120",
		("Registration No") + ":data:120",
		("Location")+":data:120",
		("Initial KM/H Reading")+":data:100",
		("Final KM/H Reading")+":data:100",
		("KM")+":data:100",
		("Hour")+":data:100",
		("HSD Drawn(L)")+":data:100",
		("Previous Balance(L)")+":data:100",
		("Total HSD(L)")+":data:100",
		("Per KM")+":data:110",
		("Per Hour")+":data:110",
		("HSD Consumption(L)")+":data:110",
		("Closing Balance(L)")+":data:110",
		("Tank Capacity")+":data:110",
		("Rate(Nu.)")+":currency:100",
		("Amount(Nu.)")+":Currency:100",

	]
	return cols
