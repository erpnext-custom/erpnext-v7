// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Penalty Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
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
