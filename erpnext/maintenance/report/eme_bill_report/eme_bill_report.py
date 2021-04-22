# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	# frappe.msgprint(format(data))
	return columns, data

def get_data(filters):
	# frappe.throw(format(filters.name))
	# SELECT DISTINCT(epi.equipment_type), ep.branch,ep.posting_date FROM `tabEME Payment` ep, `tabEME Payment Item` epi WHERE epi.parent = ep.name and  ep.name = 'EP210400007';
	return frappe.db.sql("""
		SELECT 	branch,
				posting_date,
				ep.supplier,
				ep.from_date,
				ep.to_date, 
				equipment_type,
			(SELECT count(DISTINCT equipment_no) 
				FROM `tabEME Payment Item` 
				WHERE parent = ep.name and equipment_type = ep.equipment_type) AS no,
			(SELECT SUM(total_hours) 
				FROM `tabEME Payment Item` 
				WHERE parent = ep.name and equipment_type = ep.equipment_type) AS total_hours,
			(SELECT rate 
				FROM `tabEME Payment Item` 
				WHERE parent = ep.name and equipment_type = ep.equipment_type limit 1) AS rate,
				ep.name,
				ep.tds_percent,
				ep.tds_amount,
				ep.total_amount,
				ep.deduction_amount,
				ep.payable_amount,
				ep.remarks   
			FROM (SELECT DISTINCT(epi.equipment_type),          
         	 	ep.branch,
				ep.posting_date, 
				ep.name,
				ep.from_date,
				ep.to_date,
				ep.supplier,
				ep.tds_percent,
				ep.tds_amount,
				ep.total_amount,
				ep.deduction_amount,
				ep.payable_amount,
				ep.remarks 
          	FROM `tabEME Payment` ep, `tabEME Payment Item` epi  
          	WHERE epi.parent = ep.name and  ep.name = '{}') ep;
			""".format(filters.name), as_dict=True)

def get_columns():
	return [
		_("Branch")+":Link/Branch:120",
		_("Posting Date")+":Date:120",
		_("Supplier")+":Link/Supplier:120",
		_("From Date")+":Date:120",
		_("To Date")+":Date:120",
		_("Equipment Type")+":Link/Equipment Type:120",
		_("Nos")+":Float:120",
		_("Total Hours")+":Float:120",
		_("Rate")+":Currency:120"
	]