// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Party Wise Billing"] = {
		"filters": [
			{
				"fieldname":"branch",
				"label": ("Branch"),
				"fieldtype": "Link",
				"options" : "Branch",
				
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

			},

			{
                        "fieldname": "not_cdcl",
                        "label": ("Include Only CDCL Equipments"),
                        "fieldtype": "Check",
                        "default": 1
                	},

			{	
                        "fieldname": "include_disabled",
                        "label": ("Include Disbaled Equipments"),
                        "fieldtype": "Check",
                        "default": 0
                	},

		]
	}
