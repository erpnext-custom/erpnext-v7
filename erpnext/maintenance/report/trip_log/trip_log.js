// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Trip Log"] = {
	"filters": [
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options":"Branch",
			"width": 200
		},
		{
			"fieldname":"warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options":"Warehouse",
			"width": 200
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": 200,
			"default":frappe.datetime.month_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": 200,
			"default":frappe.datetime.month_end()
		}
	]
}
