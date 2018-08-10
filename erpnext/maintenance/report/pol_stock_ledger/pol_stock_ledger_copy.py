# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.maintenance.report.maintenance_report import get_pol_till, get_pol_consumed_till
from operator import itemgetter, attrgetter

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

	query += " order by `date`"

	# get_pol_till(purpose, equipment, date, pol_type=None)
	for eq in frappe.db.sql(query, as_dict=True):
		item = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where `name`= \'" + str(eq.pol_type) + "\'", as_dict=True)
	#	if eq.reference_type == "POL":
	#		direct_consumption = frappe.db.sql("select direct_consumption from tabPOL where `name` = \'" + str(eq.reference_name) + "\'", as_dict=True)
	#		if direct_consumption[0]['direct_consumption'] == 1:
	#			dc = "Yes"
	#		else:
	#			dc = "No"
	#	else:
	#		dc = "No"
		
		if eq.reference_type == "POL":
			dtls = frappe.db.sql("select direct_consumption, branch as rec_branch from tabPOL where `name` = \'" + str(eq.reference_name) + "\'", as_dict=True)
			if dtls[0]['direct_consumption'] == 1:
				dc = "Yes"
			else:
				dc = "No"
			receiving_branch = dtls[0]['rec_branch']
		elif eq.reference_type == "Issue POL":
			if eq.type == "Receive":
				dtls = frappe.db.sql("select branch as rec_branch from `tabIssue POL` where `name` = \'" + str(eq.reference_name) + "\'", as_dict=True)
				receiving_branch = dtls[0]['rec_branch']
			else:
				receiving_branch = "NA"
			dc = "No"
		elif eq.reference_type == "Equipment POL Transfer":
			dtls = frappe.db.sql("select from_branch as rec_branch from `tabEquipment POL Transfer` where `name` = \'" + str(eq.reference_name) + "\'", as_dict=True)
			receiving_branch = dtls[0]['rec_branch']
			dc = "No"
		else:
			dc = "No"
			receiving_branch = "NA"

		received = get_pol_till("Receive", eq.equipment, eq.date, eq.pol_type)
		equipment = frappe.db.sql("select e.name, e.branch, e.equipment_number as equipment_number, et.is_container as is_container from tabEquipment e, `tabEquipment Type` et where e.equipment_type = et.name and e.name = \'" + str(eq.equipment) + "\'", as_dict=True)	
		#frappe.throw(_(" Test : {0}".format(equipment[0]['is_container'])))	
		if equipment[0]['is_container'] == 1:
			stock = get_pol_till("Stock", eq.equipment, eq.date, eq.pol_type)
			issued = get_pol_till("Issue", eq.equipment, eq.date, eq.pol_type)
			balance = flt(stock) - flt(issued)
		else:
			balance = 0

		consumed_till = get_pol_consumed_till(eq.equipment, eq.date)
		fuel_balance = flt(received) - flt(consumed_till)
		#frappe.throw(_(" Test : {0}".format(eq.reference_name)))	
		
		row = [eq.date, eq.posting_time, eq.branch, eq.equipment, equipment[0]['equipment_number'], item[0]['item_name'], item[0]['stock_uom'], eq.qty, balance, fuel_balance, eq.type, eq.reference_type, eq.reference_name,dc, receiving_branch]
		data.append(row)
		

	query1 = "select * from `tabVehicle Logbook` where docstatus = 1 "
	
	if filters.from_date and filters.to_date:
		query1 += " and to_date between \'" + str(filters.from_date) + "\' and \'" + str(filters.to_date) + "\'"
    
	if filters.branch:
		query1 += " and branch = \'" + str(filters.branch) + "\'"

	query1 += " order by `to_date`"
	
	for vl in frappe.db.sql(query1, as_dict=True):
		vitem = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where `name`= \'" + str(vl.pol_type) + "\'", as_dict=True)
		vequipment = frappe.db.sql("select e.name, e.branch, e.equipment_number as equipment_number, et.is_container as is_container from tabEquipment e, `tabEquipment Type` et where e.equipment_type = et.name and e.name = \'" + str(vl.equipment) + "\'", as_dict=True)	
		vreceived = get_pol_till("Receive", vl.equipment, vl.to_date, vl.pol_type)
		if vequipment[0]['is_container'] == 1:
			vstock = get_pol_till("Stock", vl.equipment, vl.to_date,vl.pol_type)
			vissued = get_pol_till("Issue", vl.equipment, vl.to_date, vl.pol_type)
			vbalance = flt(vstock) - flt(vissued)
		else:
			vbalance = 0

		vconsumed_till = get_pol_consumed_till(vl.equipment, vl.to_date)
		vfuel_balance = flt(vreceived) - flt(vconsumed_till)
		# frappe.throw(_(" Test : {0}".format(vl)))
		row = [vl.to_date, vl.to_time, vl.branch, vl.equipment, vequipment[0]['equipment_number'], vitem[0]['item_name'], vitem[0]['stock_uom'], vl.qty, vbalance, vfuel_balance, "Consumed", "Vehicle Logbook", vl.name, "No", "NA"]
		data.append(row)
		data = sorted(data, key=itemgetter(0,1))
		#data.sort(key=lambda r:(r[0],[1]))
	return data

def get_columns():
	return [
		("Date") + ":Date:100",
		("Time") + ":Time:100",
		("Branch") + ":Data:120",
		("Equipment") + ":Link/Equipment:100",
		("equipment No.") + ":Data:100",
		("Item Name") + ":Data:130",
		("Item UoM") + ":Data:50",
		("Qty") + ":Float:50",
		("Tanker Balance") + ":Float:100",
		("Fuel Tank Balance") + ":Float:100",
		("Purpose") + ":Data:100",
		("Reference") + ":Data:100",
		("Transaction No.") + ":Dynamic Link/"+_("Reference")+":100",
		("Direct Consumption") + ":Data:50",
		("Transaction Branch") + ":Data:100"
	]

