// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Imprest Register"] = {
	"filters": [
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
		},
		{
			"fieldname": "imprest_type",
			"label": __("Imprest Type"),
			"fieldtype": "Link",
			"options": "Imprest Type"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
	]
}
