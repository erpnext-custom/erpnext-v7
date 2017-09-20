// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Bank Guarantee Report"] = {
	"filters": [
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
