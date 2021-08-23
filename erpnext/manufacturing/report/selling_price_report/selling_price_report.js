// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Selling Price Report"] = {
	"filters": [
		{
			"fieldname":"date",
			"label": ("Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		// {
		// 	"fieldname":"to_date",
		// 	"label": ("Date"),
		// 	"fieldtype": "Date",
		// 	"reqd": 1
		// },
		{
			"fieldname": "branch",
            "label": ("Branch"),
        	"fieldtype": "Link",
            "options": "Branch",
            // "get_query": function() {
			// 		return {"doctype": "Branch", "filters": {"is_disabled": 0}}
			// },
			 "reqd":1
		},
		{
			"fieldname":"item",
			"label": ("Product"),
			"fieldtype": "Link",
			"options": "Item",
			// "get_query": function() {
			// 	var branch = frappe.query_report.filters_by_name.branch.get_value();
			// 	if(branch)
			// 		return {"doctype": "Employee", "filters": {"branch": branch }} 
			// 	}	
		}

	]
}
