// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Summarized Employee Report"] = {
	"filters": [
		
	{	
		"fieldname" :"branch",
		"label" :("Branch"),
		"fieldtype" : "Link",
		"options" : "Branch"
	},
	{
                "fieldname" :"employment_type",
                "label" :("Employment Type"),
                "fieldtype" : "Link",
                "options" : "Employment Type"
        },
	{
                "fieldname" :"designation",
                "label" :("Designation"),
                "fieldtype" : "Link",
                "options" : "Designation"
        }
	]
}
