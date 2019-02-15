# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns = get_columns(filters) 
	data = get_data(filters)
	return columns, data

def get_data(filters):
        data = []
        conditions = get_conditions(filters)

        group_by = get_group_by(filters)
        order_by = get_order_by(filters)
        total_qty = '1'
        if filters.show_aggregate:
                total_qty = "sum(qty) as total_qty"

        query = "select pe.posting_date, pe.item_code, pe.item_name, pe.item_group, pe.item_sub_group, pe.qty, pe.uom, pe.branch, pe.location, pe.adhoc_production, pe.company, pe.warehouse, pe.timber_class, pe.timber_type, pe.timber_species, cc.parent_cost_center as region, {0} from `tabProduction Entry` pe, `tabCost Center` cc where cc.name = pe.cost_center {1} {2} {3}".format(total_qty, conditions, group_by, order_by)
        abbr = " - " + str(frappe.db.get_value("Company", filters.company, "abbr"))

        total_qty = 0
        for a in frappe.db.sql(query, as_dict=1):
                if filters.show_aggregate:
                        a.qty = a.total_qty
                total_qty += flt(a.qty)
                data.append(a)
        data.append({"qty": total_qty, "branch": frappe.bold("TOTAL")})

        return data




def get_columns(filters):
        columns = [
                {
                        "fieldname": "branch",
                        "label": "Branch",
                        "fieldtype": "Link",
                        "options": "Branch",
                        "width": 120
                },
                {
                        "fieldname": "location",
                        "label": "Location",
                        "fieldtype": "Link",
                        "options": "Location",
                        "width": 120
                },
                {
                        "fieldname": "item_group",
                        "label": "Group",
                        "fieldtype": "Data",
                        "width": 120
                },
                {
                        "fieldname": "item_code",
                        "label": "Material Code",
                        "fieldtype": "Link",
                        "options": "Item",
                        "width": 150
                },
]
