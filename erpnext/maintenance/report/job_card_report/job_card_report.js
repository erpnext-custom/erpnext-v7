// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Job Card Report"] = {
	"filters": [

		{
			"fieldname":"cost_center",
			"label": ("Cost Center"),
			"fieldtype": "Link",
			"options" : "Cost Center"

		},

		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",

		},

		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",

		}

	]
}
