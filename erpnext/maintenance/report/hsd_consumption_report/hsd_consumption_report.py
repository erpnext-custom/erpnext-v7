# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from frappe.utils.data import get_last_day
from erpnext.maintenance.report.maintenance_report import get_pol_till, get_pol_between, get_pol_consumed_till

def execute(filters=None):
	columns = get_columns()
	#query = construct_query(filters)
	data = get_data(filters)

	return columns,data

def get_data(filters):
	data = []
	if filters.get("branch"):
                branch_cond =  " and eh.branch = \'" + str(filters.branch) + "\'"
        else:
                branch_cond = " and eh.branch = eh.branch" 

	if filters.get("from_date") and filters.get("to_date"):
                vl_date = " and vl.from_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\' and vl.to_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) + "\'"

		eh_cond = " and (('{0}' between eh.from_date and ifnull(eh.to_date, now())) or ('{1}' between eh.from_date and ifnull(eh.to_date, now())))".format(filters.get("from_date"), filters.get("to_date"))
        if filters.get("not_cdcl"):
               not_cdcll = " and e.not_cdcl = 0"
	else:
			   not_cdcll = ""

        if filters.get("include_disabled"):
                dis = " "
        else:
                dis = " and e.is_disabled = 0"
	if filters.get("category"):
		cat = " and e.equipment_category = '{0}'".format(filters.get("category"))
	else: cat = " and e.equipment_category = e.equipment_category"

       	#query += " GROUP BY e.equipment_number, eh.branch "
	datas = ''
	query = ''
	date = str(filters.from_date).split("-")
	from_date = date[0]+"-"+date[1]+"-"+"01"
	to_date = get_last_day(from_date)
	equipments = frappe.db.sql("""
                        select e.name as name, eh.branch as branch, e.hsd_type, e.equipment_number as equipment_number, 
                                        e.equipment_type as equipment_type, e.hsd_type, e.equipment_model as equipment_model
                                        from `tabEquipment` e, `tabEquipment History` eh 
                                        where eh.parent = e.name
                                        {0} {1} {2} {3} {4}
                                         group by eh.branch, eh.parent order by eh.branch, eh.parent
                                """.format(not_cdcll, branch_cond, dis, eh_cond, cat), as_dict = True, debug =1)
	for eq in equipments:
		query = """ select '{0}' as name, '{1}' as ty, '{2}' as no, '{3}' as br, vl.branch, ifnull(MIN(vl.initial_km),0)  AS mink, ifnull(MAX(vl.final_km),0) AS maxk, ifnull(MIN(vl.initial_hour),0) as minh, 
                	ifnull(MAX(vl.final_hour),0) as maxh, ifnull(vl.consumption_km,0) as ckm, ifnull(vl.consumption_hours,0) as ch,
                	(select ifnull((sum(pol.qty*pol.rate)/sum(pol.qty)),0) from tabPOL pol 
                        where pol.equipment_number = '{2}' and pol.posting_date between '{7}' and '{8}') as rate,
                	(select em.tank_capacity from  `tabEquipment Model` em where em.name = '{5}') as cap, 
                	CASE
			WHEN vl.ys_km THEN vl.ys_km
			else 0
			end as yskm,
			CASE
			WHEN vl.ys_hours THEN vl.ys_hours
			else 0
			end as yshour,
			ifnull(sum(vl.distance_km),0) as km,
			ifnull(sum(vl.consumption),0) as consumed from
			`tabVehicle Logbook` vl where vl.equipment_number = '{2}' {6} and
			vl.docstatus = 1 having sum(vl.consumption)>0""".format(eq.name, eq.equipment_type, eq.equipment_number, eq.branch, eq.hsd_type, eq.equipment_model, vl_date, from_date, to_date)
		datas = frappe.db.sql(query, as_dict=1)
		for d in datas:
                	d.drawn = get_pol_between("Receive", d.name, filters.from_date, filters.to_date, d.hsd_type)
                	received_till = get_pol_till("Receive", d.name, filters.from_date, d.hsd_type)
                	consumed_till = get_pol_consumed_till(d.name, filters.from_date)
                	d.opening = flt(received_till) - flt(consumed_till)
                	d.closing = flt(d.opening) + flt(d.drawn) - flt(d.consumed)

                	row = [d.name, d.ty, d.no, d.br, ("{0} / {1}".format(d.mink, d.minh)), ("{0} / {1}".format(d.maxk,d.maxh)), round(flt(d.maxk)-flt(d.mink),2), round(flt(d.maxh)-flt(d.minh),2),
                round(flt(d.drawn),2), round(flt(d.opening),2), round((flt(d.drawn)+flt(d.opening)),2),
                d.yskm, d.yshour, round(d.consumed,2), round(flt(d.closing),2), flt(d.cap), round(flt(d.rate),2), round((flt(d.rate)*flt(d.consumed)),2)]
                	data.append(row)
	return data

def get_columns():
	cols = [
		("Equipment") + ":Link/Equipment:120",
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
