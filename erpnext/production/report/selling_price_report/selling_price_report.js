// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Selling Price Report"] = {
	"filters": [
		{
			"fieldname":"report_date",
			"label": __("As on Date"),
			"fieldtype": "Date",
			"default": get_today()
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname":"to_date",
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
		},		{
			"fieldname":"item_sub_group",
			"label": __("Material Sub Group"),
			"fieldtype": "Link",
			"options": "Item Sub Group"
		},
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch"
		},
		{
			"fieldname": "location",
			"label": ("Location"),
			"fieldtype": "Link",
			"options": "Location",
			"get_query": function() {
					var branch = frappe.query_report.filters_by_name.branch.get_value();
					branch = branch.replace(' - NRDCL','');
					return {"doctype": "Location", "filters": {"branch": branch, "is_disabled": 0}}
			}
		},
		{
			"fieldname":"timber_class",
			"label": __("Timber Class"),
			"fieldtype": "Link",
			"options": "Timber Class"
		},
		{
			"fieldname":"aggregate",
			"label": __("Show Aggregate"),
			"fieldtype": "Check",
			"default": 0
		},
	]
}
