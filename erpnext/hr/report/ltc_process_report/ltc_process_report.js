		// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["LTC Process Report"] = {
	"filters": [
		{
			"fieldname": "fy",
			"label": __("Fiscal Year"),							
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1,
		},
		{
			"fieldname" : "uinput",
			"label" : ("Options"),
			"fieldtype" : "Select",
			"width": "80",
			"options" : ["LTC", "PBVA", "Bonus"],
			"reqd" : 1
		} 

	]	


}
