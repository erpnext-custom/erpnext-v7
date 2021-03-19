# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  		Phuntsho		March,05,2021                       	Calaculate the fuel balance amount using POL Entry
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
	columns =  get_column()
	data = get_data(filters)
	return columns, data

def get_column(): 
	return [
		("Logbook/POL Entry") + ":Link/Vehicle Logbook: 120",
		("Type ") + ":Data:120",
        ("Equipment ") + ":Link/Equipment:120",
		("Initial KM") + ":Float:100",
		("Final KM") + ":Float:100",
		("Total KM") + ":Float:100",
		("POL Received") + ":Float:100",
		("Opening Balance") + ":Float:100",
		("Total Consumption") + ":Float:100",
		("Balance") + ":Float:100",
		("From Date") + ":Date:120",
		("To Date") + ":Date:120",
		("From Place") + ":Data:120",
		("To Place") + ":Data:120",
		("Purpose") + ":Data:120",
        ("Equipment Type") + ":Data:100",
		("Registration No.") + ":Data:100"		
    ]

def get_data(filters): 	
	data = get_vehicle_logbook_details(filters)
	pol_receive = get_pol_receive_entries(filters)
	final_data = []
	for item in pol_receive: 
		final_data.append([ item.name,"POL Entry",item.equipment,"","","",item.qty,"","","",item.date,"","","","",item.equipment_type,item.equipment_number])
	
	for item in data: 
		# POL received and consumed respectively
		received_so_far = frappe.db.sql("""
			SELECT sum(qty) as sum FROM `tabPOL Entry` 
			WHERE equipment = '{equipment}' and date <= '{date}' and type='Receive' and docstatus=1 """.format(equipment=item["equipment"],date=item["from_date"]),as_dict=True)
		
		consumed_so_far =  frappe.db.sql ("""
			SELECT sum(qty) as sum FROM `tabPOL Entry` 
			WHERE equipment = '{equipment}' and date < '{date}' and type='consumed' and docstatus=1 """.format(equipment=item["equipment"],date=item["from_date"]),as_dict=True)

		if not received_so_far[0]['sum']: received_so_far[0]['sum'] = 0 
		if not consumed_so_far[0]['sum']: consumed_so_far[0]['sum'] = 0

		opening = received_so_far[0]['sum'] - consumed_so_far[0]['sum']
		balance = opening - item["total_consumption"]
		balance = flt(balance)

		final_data.append([
			item.name,
			"Vehicle Logbook",
			item.equipment,
			item.initial_km,
			item.final_km,
			item.total_km_run,
			"",
			opening,
			item.total_consumption,
			balance,
			item.from_date,
			item.to_date,
			item.from_place,
			item.to_place,
			item.purpose,
			item.equipment_type,
			item.registration_number
		])

	final_data.sort(key= lambda x: x[10]) # sort the final list based on from date
	return final_data


def get_pol_receive_entries (filters): 
	from_date = to_date = ""
	if (filters.get("from_date")): 
		from_date = "and pe.date >= '{}'".format(filters.get("from_date"))
	if (filters.get("to_date")): 
		to_date = "and pe.date <= '{}'".format(filters.get("to_date"))

	pol_entry = frappe.db.sql("""
		SELECT 
			pe.name,
			pe.equipment, 
			pe.date, 
			pe.qty, 
			e.equipment_type,
			e.equipment_number
		FROM 
			`tabPOL Entry` as pe,
			`tabEquipment` as e
		WHERE 
			e.name = pe.equipment and
			pe.type = "Receive" and
			pe.equipment = '{}' {} {}
		ORDER BY
			pe.date ASC
		""".format(filters.get("equipment_no"), from_date, to_date), as_dict=1)
	return pol_entry


def get_vehicle_logbook_details(filters):
	"""
		get details from vehicle logbook
	"""
	from_date = to_date = ""
	if (filters.get("from_date")): 
		from_date = "and vlog.from_date >= '{}'".format(filters.get("from_date"))
	if (filters.get("to_date")): 
		to_date = "and vlog.to_date <= '{}'".format(filters.get("to_date"))

	data = frappe.db.sql("""
		SELECT 
			vl.name, 
			vl.equipment , 
			vlog.initial_km , 
			vlog.final_km , 
			vlog.total_km_run , 
			vlog.total_consumption ,
			vl.equipment_type, 
			vl.registration_number, 
			vlog.from_date , 
			vlog.to_date,
			vlog.from_place, 
			vlog.to_place, 
			vlog.purpose 
		FROM `tabVehicle Logbook` as vl, `tabVehicle Log` as vlog
		WHERE vlog.parent = vl.name and vl.docstatus = 1 and vl.equipment = '{}' {} {}
		ORDER BY vlog.from_date ASC """.format(filters.get("equipment_no"), from_date, to_date), as_dict=1)
	return data
