# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint, add_days, cstr, flt, getdate, nowdate, rounded, date_diff
'''
---------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
---------------------------------------------------------------------------------------------------------------------
				PHUNTSHO		            		23/02/2021           query modified to include transport info from child table
---------------------------------------------------------------------------------------------------------------------
'''


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    cols = [
        ("Date") + ":date:100",
        ("Material Code") + ":data:110",
        ("Material Name")+":data:120",
        ("Material Group")+":data:120",
        ("UoM") + ":data:50",
        ("Qty")+":data:50",
        ("Valuation Rate")+":data:120",
        ("Amount")+":Currency:110",
    ]

    if filters.purpose in ("Material Issue", "Inventory Write Off"):
        cols.append(("Cost Center")+":data:170")
        cols.append(("Issued To Employee")+":Link/Employee:120")
        cols.append(("Issued To Equipment")+":Link/Equipment:120")

    if filters.purpose == "Material Transfer":
        cols.insert(6, {"fieldname": "received_qty",
                        "label": "Received Qty", "fieldtype": "Data", "width": 100}),
        cols.insert(7, {"fieldname": "difference_qty",
                        "label": "Difference Qty", "fieldtype": "Data", "width": 100}),
        cols.append(("Source Warehouse")+":data:170")
        cols.append(("Destination Warehouse")+":data:170")
        cols.append(("Equipment Model")+":data:140")
        cols.append(("Equipment Number")+":data:170")
    cols.append(("Stock Entry")+":Link/Stock Entry:170")
    return cols


def get_data(filters):
    if filters.purpose == 'Material Transfer':
        # data = "select se.posting_date, sed.item_code, sed.item_name, (select i.item_group from tabItem i where i.item_code = sed.item_code) as item_group, sed.uom, sed.qty, sed.received_qty, sed.difference_qty, sed.valuation_rate, sed.received_qty*sed.valuation_rate, sed.s_warehouse, sed.t_warehouse, COALESCE(se.equipment_model,sed.equipment_model)as equipment_model, COALESCE(se.equipment_number,sed.equipment_number) as equipment_number, se.name FROM `tabStock Entry` se, `tabStock Entry Detail` sed WHERE se.name = sed.parent and  se.docstatus = 1 and se.purpose = 'Material Transfer' and se.is_write_off_entry = 0"
        query = """
			SELECT
				se.posting_date,
				sed.item_code,
				sed.item_name,
				i.item_group,
				sed.uom, 
				sed.qty, 
				sed.received_qty, 
				sed.difference_qty, 
				sed.valuation_rate, 
				sed.received_qty*sed.valuation_rate as valuation_rate, 
				sed.s_warehouse, 
				sed.t_warehouse, 
				COALESCE(se.equipment_model,sed.equipment_model)as equipment_model, 
				COALESCE(se.equipment_number,sed.equipment_number) as equipment_number, 
				se.name 
			FROM 
				`tabStock Entry` se
			INNER JOIN  
				`tabStock Entry Detail` sed 
			ON 
				se.name = sed.parent
			INNER JOIN 
				`tabItem` i
			ON
				i.item_code = sed.item_code
			WHERE 
				se.docstatus = 1 
			AND 
				se.purpose = 'Material Transfer' 
			AND 
				se.is_write_off_entry = 0
		"""
    elif filters.purpose == 'Material Issue':
        # query = "select se.posting_date, sed.item_code, sed.item_name, (select i.item_group from tabItem i where i.item_code = sed.item_code) as item_group, sed.uom, sed.qty, sed.valuation_rate,sed.amount, sed.cost_center, sed.issue_to_employee,issue_to_equipment, se.name FROM `tabStock Entry` se, `tabStock Entry Detail` sed WHERE se.name = sed.parent and  se.docstatus = 1 and se.purpose = 'Material Issue' and se.is_write_off_entry = 0"
        query = """
		SELECT 
			se.posting_date, 
			sed.item_code, 
			sed.item_name, 
			i.item_group, 
			sed.uom, 
			sed.qty, 
			sed.valuation_rate,
			sed.amount, 
			sed.cost_center, 
			sed.issued_to_employee,
			sed.issued_to_equipment, 
			se.name 
		FROM `tabStock Entry` se 
		INNER JOIN 
			`tabStock Entry Detail` sed 
		ON
			se.name = sed.parent
		INNER JOIN 
			`tabItem` i
		ON i.item_code = sed.item_code
		WHERE 
			se.docstatus = 1 
		AND 
			se.purpose = 'Material Issue' 
		AND 
			se.is_write_off_entry = 0
		"""
    elif filters.purpose == 'Inventory Write Off':
        # query = "select se.posting_date, sed.item_code, sed.item_name, (select i.item_group from tabItem i where i.item_code = sed.item_code) as item_group, sed.uom, sed.qty, sed.valuation_rate,sed.amount, sed.cost_center, sed.issue_to_employee,issue_to_equipment, se.name FROM `tabStock Entry` se, `tabStock Entry Detail` sed WHERE se.name = sed.parent and  se.docstatus = 1 and se.purpose = 'Material Issue' and se.is_write_off_entry = 1"
        query = """
			SELECT 
				se.posting_date, 
				sed.item_code, 
				sed.item_name,
				i.item_group, 
				sed.uom, 
				sed.qty, 
				sed.valuation_rate,
				sed.amount, 
				sed.cost_center, 
				se.name 
			FROM 
				`tabStock Entry` se 
			INNER JOIN 
				`tabStock Entry Detail` sed 
			ON 
				se.name = sed.parent 
			INNER JOIN 
				`tabItem` i 
			ON 
				i.item_code = sed.item_code
			AND
				se.docstatus = 1 
			AND 
				se.purpose = 'Material Issue' 
			AND 
				se.is_write_off_entry = 1
			"""
    if filters.get("warehouse"):
        query += " AND sed.s_warehouse = '{0}' ".format(filters.warehouse)
    if filters.get("item_code"):
        query += " AND sed.item_code = '{0}' ".format(filters.item_code)
    if filters.get("from_date") and filters.get("to_date"):
        query += " AND se.posting_date between '{0}' AND '{1}' ".format(filters.from_date,filters.to_date)
    if filters.get("equipment_type"):
        query += " and COALESCE(se.equipment_type,sed.equipment_type) = '{0}'".format(filters.equipment_type)
    query += " ORDER BY se.posting_date ;"
    return frappe.db.sql(query)
