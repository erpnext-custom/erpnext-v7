
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, formatdate, cstr
from erpnext.maintenance.report.maintenance_report import get_pol_till 

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data

def get_data(filters=None):
	data = []
	cond = "('{0}' between eh.from_date and ifnull(eh.to_date, now()))".format(filters.get("to_date"))
	query = "select e.name, eh.branch, e.equipment_number from tabEquipment e, `tabEquipment Type` et, `tabEquipment History` eh  where e.equipment_type = et.name and et.is_container = 1 and e.name = eh.parent and {0}".format(cond)
	if filters.branch:
		query += " and eh.branch = \'" + str(filters.branch) + "\'"
		
	items = frappe.db.sql("select item_code, item_name, stock_uom from tabItem where is_hsd_item = 1 and disabled = 0", as_dict=True)

	query += " order by eh.branch"
	# frappe.msgprint("{0}".format(query))
	for eq in frappe.db.sql(query, as_dict=True):
		for item in items:
			received = get_pol_till("Receive", eq.name, filters.to_date, item.item_code)
			issued = get_pol_till("Issue", eq.name, filters.to_date, item.item_code)
			if received or issued:
				row = [eq.name, eq.equipment_number, eq.branch, item.item_code, item.item_name, item.stock_uom, received, issued, flt(received) - flt(issued)]
				data.append(row)
	return data

def get_columns():
	return [
		{
			"fieldname": "equipment",
			"label": _("Equipment"),
			"fieldtype": "Link",
			"options": "Equipment",
			"width": 100
		},
		{
                        "fieldname": "eq_name",
                        "label": _("Equipment Name"),
                        "fieldtype": "Data",
                        "width": 130
                },
		{
                        "fieldname": "branch",
                        "label": _("Branch"),
                        "fieldtype": "Link",
                        "options": "Branch",
                        "width": 200
                },
		{
                        "fieldname": "pol_type",
                        "label": _("Item Code"),
                        "fieldtype": "Data",
                        "width": 100
                },
		{
                        "fieldname": "pol_name",
                        "label": _("Item Name"),
                        "fieldtype": "Data",
                        "width": 170
                },
		{
                        "fieldname": "uom",
                        "label": _("UOM"),
                        "fieldtype": "Link",
                        "options": "UOM",
                        "width": 60
                },
		{
                        "fieldname": "received",
                        "label": _("Received"),
                        "fieldtype": "Float",
                        "width": 100
                },
		{
                        "fieldname": "issued",
                        "label": _("Issued"),
                        "fieldtype": "Float",
                        "width": 100
                },
		{
                        "fieldname": "balance",
                        "label": _("Balance"),
                        "fieldtype": "Float",
                        "width": 100
                },
	]
