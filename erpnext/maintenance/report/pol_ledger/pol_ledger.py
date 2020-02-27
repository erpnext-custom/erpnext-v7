# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr, get_datetime
from erpnext.maintenance.report.maintenance_report import get_pol_till, get_pol_consumed_till
from operator import itemgetter, attrgetter
import datetime

def execute(filters=None):
	columns = get_columns();
	data = get_data(filters);

	return columns, data

def get_data(filters=None):
	data = []
	query = "select * from `tabPOL Entry` where docstatus = 1 "
	
	if filters.from_date and filters.to_date:
		query += " and date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
    
	if filters.branch:
		query += " and branch = \'" + str(filters.branch) + "\'"

	if filters.equipment:
		query += " and equipment = \'" + str(filters.equipment) + "\'"

	query += " order by `date`"
	# get_pol_till(purpose, equipment, date, pol_type=None)
	for eq in frappe.db.sql(query, as_dict=True):
		item = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where `name`= \'" + str(eq.pol_type) + "\'", as_dict=True)
	
		branch = frappe.db.get_value(eq.reference_type, eq.reference_name, "branch")
		dc = "No"
		if eq.reference_type == "POL":
			pol = frappe.get_doc(eq.reference_type, eq.reference_name)
			if pol.direct_consumption:
				dc = "Yes"
	
#		get_pol_till(purpose, equipment, posting_date, pol_type=None, own_cc=None, posting_time="24:00"):
		received = get_pol_till("Receive", eq.equipment, eq.date, eq.pol_type, posting_time=eq.posting_time )
		equipment = frappe.db.sql("select e.name, e.branch, e.equipment_type as equipment_type,  e.equipment_number as equipment_number, et.is_container as is_container from tabEquipment e, `tabEquipment Type` et where e.equipment_type = et.name and e.name = \'" + str(eq.equipment) + "\'", as_dict=True)	
		#frappe.throw(_(" Test : {0}".format(equipment[0]['is_container'])))	
		if equipment[0]['is_container'] == 1:
			stock = get_pol_till("Stock", eq.equipment, eq.date, eq.pol_type, posting_time=eq.posting_time)
			issued = get_pol_till("Issue", eq.equipment, eq.date, eq.pol_type, posting_time=eq.posting_time)
			balance = flt(stock) - flt(issued)
		else:
			balance = 0

		consumed_till = get_pol_consumed_till(eq.equipment, eq.date, eq.posting_time)
		if equipment[0]['equipment_type'] == "Barrel":
			fuel_balance = 0
		else:
			fuel_balance = flt(received) - flt(consumed_till)
                if eq.type == "Issue":
			trans_qty = -eq.qty
		else:
			trans_qty = eq.qty

		row = [get_datetime(str(eq.date) + " " + str(eq.posting_time)), eq.branch, eq.equipment, equipment[0]['equipment_number'], item[0]['item_name'], trans_qty, fuel_balance, balance, eq.type, eq.reference_type, eq.reference_name, branch, dc]
		data.append(row)
		

	query1 = "select * from `tabVehicle Logbook` where docstatus = 1 "
	
	if filters.from_date and filters.to_date:
		query1 += " and to_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
    
	if filters.branch:
		query1 += " and branch = \'" + str(filters.branch) + "\'"

	if filters.equipment:
		query1 += " and equipment = \'" + str(filters.equipment) + "\'"

	query1 += " order by `to_date`"
	
	for vl in frappe.db.sql(query1, as_dict=True):
#		vitem = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where `name`= \'" + str(vl.pol_type) + "\'", as_dict=True)
		vequipment = frappe.db.sql("select e.name, e.branch, e.equipment_number as equipment_number, e.hsd_type as pol_type, et.is_container as is_container from tabEquipment e, `tabEquipment Type` et where e.equipment_type = et.name and e.name = \'" + str(vl.equipment) + "\'", as_dict=True)	
		epol_type = vequipment[0]['pol_type']
		
		vitem = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where `name`= \'" + str(epol_type) + "\'", as_dict=True)
		vreceived = get_pol_till("Receive", vl.equipment, vl.to_date, epol_type, posting_time= vl.to_time)
		if vequipment[0]['is_container'] == 1:
			vstock = get_pol_till("Stock", vl.equipment, vl.to_date, epol_type, posting_time= vl.to_time)
			vissued = get_pol_till("Issue", vl.equipment, vl.to_date, epol_type, posting_time= vl.to_time)
			vbalance = flt(vstock) - flt(vissued)
		else:
			vbalance = 0

		vconsumed_till = get_pol_consumed_till(vl.equipment, vl.to_date, vl.to_time)
		vfuel_balance = flt(vreceived) - flt(vconsumed_till)
		row = [get_datetime(str(vl.to_date) + " " + str(vl.to_time)), vl.branch, vl.equipment, vequipment[0]['equipment_number'], vitem[0]['item_name'], -vl.consumption, vfuel_balance, vbalance, "Consumed", "Vehicle Logbook", vl.name, vl.branch, "No"]
		data.append(row)

	data = sorted(data, key=itemgetter(0))
		#data.sort(key=lambda r:(r[0],[1]))
	return data

def get_columns():
	return [
		("Date & Time") + ":Date:140",
		("Branch") + ":Data:120",
		("Equipment") + ":Link/Equipment:100",
		("Equipment No.") + ":Data:100",
		("Item Name") + ":Link/Item:130",
		("Qty") + ":Float:80",
		("Fuel Tank Balance") + ":Float:100",
		("Tanker Balance") + ":Float:100",
		("Purpose") + ":Data:90",
		("Reference") + ":Data:100",
		("Transaction No.") + ":Dynamic Link/"+_("Reference")+":120",
		("Transaction Branch") + ":Data:130",
		("Direct Consumption") + "Data:50"
	]
