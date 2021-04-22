// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Information"] = {
	"filters": [
		{
			fieldname: "company",
			label: "Company",
			fieldtype: "Link",
			options: "Company",
			width: 200
			// default:"Select Material Type"
		},
		{
			fieldname: "employment_type",
			label: "Employment Type",
			fieldtype: "Link",
			options: "Employment Type",
			width: 200
		},
		{
			fieldname: "status",
			label: "Status",
			fieldtype: "Select",
			options: ["All", "Active", "Left"],
			default: "All"
		}
	]
}
