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
		if eq.reference_type == "POL":
			direct_consumption = frappe.db.sql("select direct_consumption from tabPOL where `name` = \'" + str(eq.reference_name) + "\'", as_dict=True)
			if direct_consumption[0]['direct_consumption'] == 1:
				dc = "Yes"
			else:
				dc = "No"
		else:
			dc = "No"

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
		
		row = [eq.date, eq.posting_time, eq.branch, eq.equipment, equipment[0]['equipment_number'], item[0]['item_name'], item[0]['stock_uom'], eq.qty, balance, fuel_balance, eq.type, eq.reference_name, dc, eq.reference_type]
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
		row = [vl.to_date, vl.to_time, vl.branch, vl.equipment, vequipment[0]['equipment_number'], vitem[0]['item_name'], vitem[0]['stock_uom'], vl.qty, vbalance, vfuel_balance, "Consumed", vl.name, "No", "Vehicle Logbook"]
		data.append(row)
		data = sorted(data, key=itemgetter(0,1))
		#data.sort(key=lambda r:(r[0],[1]))
	return data

def get_columns():
	return [
		{
			"fieldname": "posting_date",
			"label": _("Date"),
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "time",
			"label": _("Time"),
			"fieldtype": "Time",
			"width": 100
		},
		{
			"fieldname": "branch",
			"label": _("Equipment Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": 120
		},
		{
			"fieldname": "equipment",
			"label": _("Equipment"),
			"fieldtype": "Link",
			"options": "Equipment",
			"width": 100
		},
		{
			"fieldname": "equipment_no",
			"label": _("Equipment No"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "item",
			"label": _("Item Name"),
			"fieldtype": "Data",
			"width": 130
		},
		{
			"fieldname": "uom",
			"label": _("UoM"),
			"fieldtype": "Data",
			"width": 50
		},
		{
			"fieldname": "qty",
			"label": _("Qty"),
			"fieldtype": "Float",
			"width": 50
		},
		{
			"fieldname": "balance",
			"label": _("Tanker Balance"),
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "fuel_tank_balance",
			"label": _("Fuel Tank Balance"),
			"fieldtype": "Float",
			"width": 100 
		},
		{
			"fieldname": "type",
			"label": _("Purpose"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "transaction",
			"label": _("Transaction No"),
			"fieldtype": "Link",
			"options": "",
			"width": 100
		},
		{
			"fieldname": "direct_consumption",
			"label": _("Direct Consumption"),
			"fieldtype": "Data",
			"width": 50
		},
                {
			"fieldname": "reference_type",
			"label": _("Reference"),
			"fieldtype": "Data",
			"width": 100
		}
	]

