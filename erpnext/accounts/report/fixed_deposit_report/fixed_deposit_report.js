// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Fixed Deposit Report"] = {
	"filters": [
		{
		
			"fieldname":"branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100",
		
		},
		{	
			"fieldname" : "from_date",
			"label" : ("From Date"),
			"fieldtype" : "Date",
		},
		{
			"fieldname" : "to_date",
			"label" : ("To Date"),
			"fieldtype" : "Date",
		},
		

	]
}
