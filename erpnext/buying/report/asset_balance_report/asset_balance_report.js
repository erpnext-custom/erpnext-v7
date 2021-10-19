// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Asset Balance Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
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
                }
	],
}
