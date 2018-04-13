from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint,add_days, cstr, flt, getdate, nowdate, rounded, date_diff

def get_pol_received_till(equipment, date, pol_type=None):
	if not pol_type:
		pol_type = '%'
	if not equipment or not date:
		frappe.throw("Equipment and Till Date are Mandatory")
	
	pol = frappe.db.sql("select sum(qty) as total from `tabConsumed POL` where equipment = %s and docstatus = 1 and date <= %s and pol_type like %s", (equipment, date, pol_type), as_dict=True)
	if pol:
		return pol[0].total
	else:
		return 0

def get_pol_consumed_till(equipment, date):
	if not equipment or not date:
                frappe.throw("Equipment and Till Date are Mandatory")
	pol = frappe.db.sql("select sum(consumption) as total from `tabVehicle Logbook` where docstatus = 1 and equipment = %s and to_date <= %s", (equipment, date), as_dict=True)
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

def get_employee_expense(equipment, f_date, t_date):
	if not equipment or not f_date or not t_date:
                frappe.throw("Equipment and From/Till Date are Mandatory")

	operators = frappe.db.sql("""
			select operator, employee_type, start_date, end_date
			from `tabEquipment Operator`
			where parent = '{0}' 
			and   docstatus < 2
			and   (start_date between {1} and {2} OR end_date between {3} and {4})
		""".format(equipment, f_date, t_date, f_date, t_date), as_dict=1)

	for a in operators:
		prorate_fraction = 1
		if getdate(f_date) < getdate(a.start_date) and getdate(t_date) > getdate(a.end_date):
		# Pay

		# Bonus

		# PBVA

		# Travel

		#Leave Encashment

	



