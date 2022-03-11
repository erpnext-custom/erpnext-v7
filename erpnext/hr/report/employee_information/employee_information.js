// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Information"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": "Company",
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
		},
		{
            fieldname: "status",
            label: "Status",
            fieldtype: "Select",
            options:["", "Active", "Left"]
		},
		{
			fieldname: "employment_type",
			label: "Employment Type",
			fieldtype: "Link",
			options: "Employment Type",
		},
		{
			"fieldname": "accumulate_data",
			"label": "Accumulated Data",
			"fieldtype": "Check",
		},
		{
			"fieldname": "qualification",
			"label": "Include Qualification",
			"fieldtype": "Check",
		},
	]
}
