// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Material Balance History"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": sys_defaults.year_start_date,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},
		/*{
                        "fieldname":"cost_center",
                        "label": __("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center"
                },*/
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
