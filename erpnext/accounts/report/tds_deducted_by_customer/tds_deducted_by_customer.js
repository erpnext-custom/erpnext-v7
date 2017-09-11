// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["TDS Deducted By Customer"] = {
	"filters":[
		{
			"fieldname" : "from_date",
			"label":("From Date"),
			"fieldtype" : "Date",
			"width" : "80",
			"reqd" :1,
		},
		{
			"fieldname" : "to_date",
			"label":("To Date"),
			"fieldtype" : "Date",
			"width" : "80",
			"reqd" :1,
		},
	]
}
