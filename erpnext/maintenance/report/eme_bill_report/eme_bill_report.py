# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = get_columns(), get_data(filters)
	return columns, data

def get_data(filters):
	# frappe.throw(format(filters.name))
	# SELECT DISTINCT(epi.equipment_type), ep.branch,ep.posting_date FROM `tabEME Payment` ep, `tabEME Payment Item` epi WHERE epi.parent = ep.name and  ep.name = 'EP210400007';
	return frappe.db.sql("""
		SELECT equipment_type,
				branch,
				posting_date,
				ep.from_date,
				ep.to_date, 
				ep.supplier,
				ep.name as ref,
				ep.tds_percent,
				ep.tds_amount,
				ep.total_amount,
				ep.deduction_amount,
				ep.payable_amount,
				ep.remarks,
			(SELECT count(DISTINCT equipment_no) 
				FROM `tabEME Payment Item` 
				WHERE parent = ep.name and equipment_type = ep.equipment_type) AS no,
			(SELECT 
				CASE
					WHEN (new_rate IS NULL or new_rate = "") THEN rate
					ELSE (new_rate - prev_rate)
				END
				FROM `tabEME Payment Item` 
				WHERE rate > 0 and parent = ep.name and equipment_type = ep.equipment_type limit 1) AS rate,
			(SELECT SUM(total_hours) 
				FROM `tabEME Payment Item` 
				WHERE parent = ep.name and equipment_type = ep.equipment_type 
				and rate > 0) AS total_hours   
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
          	WHERE epi.parent = ep.name and  ep.name = '{}' and epi.rate > 0) ep;
			""".format(filters.name),as_dict=True)

def get_columns():
	return [
		{
			"fieldname":"branch",
			"label":_("Branch"),
			"fieldtype":"Link",
			"options":"Branch",
			"width":120
		},
		{
			"fieldname":"posting_date",
			"label":_("Posting Date"),
			"fieldtype":"Date",
			"width":120
		},
		{
			"fieldname":"supplier",
			"label":_("Supplier"),
			"fieldtype":"Link",
			"options":"Supplier",
			"width":120
		},
		{
			"fieldname":"from_date",
			"label":_("From date"),
			"fieldtype":"Date",
			"width":120
		},
		{
			"fieldname":"to_date",
			"label":_("To date"),
			"fieldtype":"Date",
			"width":120
		},
		{
			"fieldname":"equipment_type",
			"label":_("Equipment Type"),
			"fieldtype":"Link",
			"options":"Equipment Type",
			"width":120
		},
		{
			"fieldname":"no",
			"label":_("Nos"),
			"fieldtype":"Float",
			"width":120
		},
		{
			"fieldname":"total_hours",
			"label":_("Total Hours"),
			"fieldtype":"Float",
			"width":120
		},
		{
			"fieldname":"rate",
			"label":_("Rate"),
			"fieldtype":"Currency",
			"width":120
		}
	]