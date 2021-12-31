from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff, get_datetime

##
# Both recieved and issued pols can be queried with this
##
def get_pol_till(purpose, equipment, from_date, to_date, pol_type=None, own_cc=None, posting_time="23:59:59"):
	if not equipment or not from_date or not to_date:
		frappe.throw("Equipment and Till Date are Mandatory")
		
	total = 0
	query = """
			select sum(qty) as total 
			from `tabPOL Entry` 
			where docstatus = 1 and type = '{}' and equipment = '{}' 
			and date >= '{}' 
			and date <= '{}'
		""".format(purpose, equipment, from_date, to_date)
	
	if pol_type:
		query += " and pol_type = \'" + str(pol_type) + "\'"
	if own_cc:
		query += " and own_cost_center = 1"

	quantity = frappe.db.sql(query, as_dict=True)
	if quantity:
		total = quantity[0].total
	return total

##
# Both recieved and issued pols can be queried with this
##
def get_pol_between(purpose, equipment, from_date, to_date, pol_type=None, own_cc=None):
	if not equipment or not from_date or not to_date:
		frappe.throw("Equipment and From/To Date are Mandatory")
	total = 0
	query = "select sum(qty) as total from `tabPOL Entry` where docstatus = 1 and type = \'"+str(purpose)+"\' and equipment = \'" + str(equipment) + "\' and date between \'" + str(from_date) + "\' and \'" + str(to_date) + "\'"
	if pol_type:
		query += " and pol_type = \'" + str(pol_type) + "\'"
	if own_cc:
		query += " and own_cost_center = 1"
		
	quantity = frappe.db.sql(query, as_dict=True)
	if quantity:
		total = quantity[0].total
	return total

##
# Get consumed POl as per yardstick
##
def get_pol_consumed_till(equipment, from_date, to_date, posting_time="23:59:59", filter_dry=None):
	if not equipment or not from_date or not to_date:
		frappe.throw("Equipment and Till Date are Mandatory")

	if not filter_dry:
		query = """	
				select sum(consumption) as total 
				from `tabVehicle Logbook` 
				where docstatus = 1 and equipment = '{}' 
				and from_date >= '{}' 
				and to_date <= '{}'
		""".format(equipment, from_date, to_date)
	else:
		query = """
				select 
					sum(consumption) as total 
				from `tabVehicle Logbook` 
				where docstatus = 1 and equipment = '{}' and rate_type = 'With Fuel' 
				and from_date >= '{}' 
				and to_date <= '{}'
		""".format(equipment, from_date, to_date)
	
	pol = frappe.db.sql(query, as_dict=True)
	if pol:
		return pol[0].total
	else:
		return 0	

def get_km_till(equipment, date):
	if not equipment or not date:
		frappe.throw("Equipment and Till Date are Mandatory")
	
	km = frappe.db.sql("select final_km from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by final_km desc limit 1", (equipment, date), as_dict=True)
	if km:
		return km[0].final_km
	else:
		return 0	
	
def get_hour_till(equipment, date):
	if not equipment or not date:
                frappe.throw("Equipment and Till Date are Mandatory")
	hr = frappe.db.sql("select final_hour from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s order by final_hour desc limit 1", (equipment, date), as_dict=True)
	if hr:
		return hr[0].final_hour
	else:
		return 0	


