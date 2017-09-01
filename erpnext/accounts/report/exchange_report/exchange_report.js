// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Exchange Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1
		},

		{
			"fieldname": "currency",
			"label": ("Currency"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Currency"
		},


	]
}
