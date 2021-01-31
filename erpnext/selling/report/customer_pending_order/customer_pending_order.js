// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Pending Order"] = {
	"filters": [

		{	
			"fieldname": "start_date",
			"label": ("Start Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{	
			"fieldname": "to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd":1
		},
		{	
			"fieldname": "customer",
			"label": ("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "80"
		},
		{	
			"fieldname": "status",
			"label": ("Status"),
			"fieldtype": "Select",
			"options": ["Pending","Delivered"],
			"default": "Pending",
			"width": "80"
		}
		

	]
}
