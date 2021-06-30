// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Material Purchase History Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname":"branch",
            "label": __("Branch"),
            "fieldtype": "Link",
        	"options": "Branch"
		}
	]
}
