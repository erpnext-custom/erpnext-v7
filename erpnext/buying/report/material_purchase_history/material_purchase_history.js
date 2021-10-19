// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Material Purchase History"] = {
	"filters": [
				 {
                        "fieldname":"from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "default": sys_defaults.year_start_date,
                        "reqd": 1
                },
                {
                        "fieldname":"to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.get_today(),
                        "reqd": 1
                },
                {
                        "fieldname":"cost_center",
                        "label": __("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center"
                },
		{
                        "fieldname":"warehouse",
                        "label": __("Warehouse"),
                        "fieldtype": "Link",
                        "options": "Warehouse"
                },
                {
                        "fieldname":"item_code",
                        "label": __("Material Code"),
                        "fieldtype": "Link",
                        "options": "Item"
                },
                {
                        "fieldname":"item_group",
                        "label": __("Material Group"),
                        "fieldtype": "Link",
                        "options": "Item Group"
                },
                {
                        "fieldname":"item_sub_group",
                        "label": __("Material Sub Group"),
                        "fieldtype": "Link",
                        "options": "Item Sub Group"
                }

	]
}
