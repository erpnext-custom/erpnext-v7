# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.data import get_first_day, get_last_day, add_days
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.maintenance.report.maintenance_report import get_km_till, get_hour_till, get_pol_till, \
	get_pol_between, get_pol_consumed_till

def execute(filters=None):
	columns = get_columns()
	query = construct_query(filters)
	data = get_data(query, filters)

	return columns,data

def get_data(query, filters=None):
	data = []
	datas = frappe.db.sql(query, as_dict=True);
	for d in datas:
		own_cc = 0
		if filters.own_cc:
			own_cc = 1
		d.drawn = get_pol_between("Receive", d.name, filters.from_date, filters.to_date, d.hsd_type, own_cc)
		received_till = get_pol_till("Receive", d.name, add_days(getdate(filters.from_date), -1), d.hsd_type)
		consumed_till = get_pol_consumed_till(d.name, add_days(getdate(filters.from_date), -1), filter_dry=own_cc)
		consumed_till_end = get_pol_consumed_till(d.name, filters.to_date, filter_dry=own_cc)
		d.consumed = flt(consumed_till_end) - flt(consumed_till)
		d.opening = flt(received_till) - flt(consumed_till)
		d.closing = flt(d.opening) + flt(d.drawn) - flt(d.consumed)
		d.open_km = get_km_till(d.name, add_days(getdate(filters.from_date), -1))
		d.open_hr = get_hour_till(d.name, add_days(getdate(filters.from_date), -1))
		d.close_km = get_km_till(d.name, filters.to_date)
		d.close_hr = get_hour_till(d.name, filters.to_date)

		d.cap = frappe.db.get_value("Equipment Model", d.equipment_model, "tank_capacity")
		rate = frappe.db.sql("select (sum(pol.qty*pol.rate)/sum(pol.qty)) as rate from tabPOL pol where pol.branch = %s and pol.docstatus = 1 and pol.pol_type = %s", (d.branch, d.hsd_type))
		d.rate = rate and flt(rate[0][0]) or 0.0
	
		vl_records = frappe.db.sql("select place from `tabVehicle Logbook` where equipment = %s and docstatus = 1 order by to_date desc limit 1", d.name, as_dict=1)
		d.place = vl_records and flt(vl_records[0].place) or ""

		ys_records = frappe.db.sql("select hci.yard_hours, hci.yard_distance from `tabHire Charge Item` hci, `tabHire Charge Parameter` hcp where hcp.name = hci.parent and hcp.equipment_type = %s and hcp.equipment_model = %s and (%s between from_date and ifnull(to_date, curdate()) or %s between from_date and ifnull(to_date, curdate()))", (d.equipment_type, d.equipment_model, filters.from_date, filters.to_date), as_dict=1)
		d.yskm = ys_records and flt(ys_records[0].yard_distance) or 0
		d.yshour = ys_records and flt(ys_records[0].yard_hours) or 0
	
		row = [d.name, d.equipment_category, d.equipment_type, d.equipment_number, d.place, ("{0}" '/' "{1}".format(d.open_km, d.open_hr)), ("{0}" '/' "{1}".format(d.close_km,d.close_hr)), round(d.close_km-d.open_km,2), round(d.close_hr-d.open_hr,2),
		round(flt(d.drawn),2), round(flt(d.opening),2), round((flt(d.drawn)+flt(d.opening)),2),
		d.yskm, d.yshour, round(d.consumed,2), round(flt(d.closing),2), flt(d.cap), round(flt(d.rate),2), round((flt(d.rate)*flt(d.consumed)),2)]
		data.append(row);
	return data
	#KM and Hour value is changed from consumption_km and consumption_hours to diference between the final and initial after discussing with Project Lead
def construct_query(filters):
	#(select (sum(pol.qty*pol.rate)/sum(pol.qty)) from tabPOL pol where pol.branch = vl.branch and pol.docstatus = 1 and pol.pol_type = e.hsd_type) as rate, e.hsd_type,
	query = """select e.name, eh.branch, e.equipment_category, e.hsd_type, e.equipment_number, e.equipment_type, e.equipment_model 
		from `tabEquipment History` eh, tabEquipment e 
		where eh.parent = e.name """
	if filters.get("branch"):
		query += " and eh.branch = \'" + str(filters.branch) + "\'"

	if filters.get("from_date") and filters.get("to_date"):
		# query += " and (eh.from_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\' or ifnull(eh.to_date, curdate()) between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\')"
		query += " and ('{0}' >= ifnull(eh.from_date, curdate()) and '{1}' <= ifnull(eh.to_date, curdate()))".format(filters.to_date, filters.from_date)
		

	if not filters.include_disabled:
                query += " and e.is_disabled = 0"

	if filters.not_cdcl:
               query += " and e.not_cdcl = 0"

	'''if filters.category:
		query += " and e.equipment_category = \'" + str(filters.category) + "\'"'''	

	query += " GROUP BY e.name, eh.branch order by e.equipment_category, e.equipment_type ASC"
	return query

def get_columns():
	cols = [
		("Equipment") + ":Link/Equipment:120",
		("Equipment Category") + ":data:120",
		("Equipment Type.") + ":data:120",
		("Registration No") + ":data:120",
		("Location")+":data:120",
		("Initial KM/H")+":data:100",
		("Final KM/H")+":data:100",
		("KM")+":Data:100",
		("Hour")+":Data:100",
		("HSD Drawn(L)")+":data:100",
		("Prev Bal(L)")+":data:100",
		("Total HSD(L)")+":data:100",
		("Per KM")+":data:110",
		("Per Hour")+":data:110",
		("HSD Consumption(L)")+":data:110",
		("Closing Bal(L)")+":data:110",
		("Tank Capacity")+":data:110",
		("Rate(Nu.)")+":currency:100",
		("Amount(Nu.)")+":Currency:100",

	]
	return cols
