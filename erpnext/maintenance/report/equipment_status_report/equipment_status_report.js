// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment Status Report"] = {
	"filters": [
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Branch",
		},
		{
			"fieldname": "uinput",
			"label": ("Options"),
			"fieldtype": "Select",
			"width": "80",
			"options": ["Free","Occupied"],
			"reqd": 1
		},
		{
			"fieldname":"equipment",
			"label": ("Equipment"),
			"fieldtype":"Link",
			"options": ("Equipment"),
			"width": "80",
		},

		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd" :1,
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
		},


	]
}
