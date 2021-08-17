// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Dispatch Report"] = {
	"filters": [
		{
			"fieldname": "dispatch_type",
			"label": "Dispatch Type",
			"fieldtype": "Select",
			"options": ["Incoming", "Out-Going"],
			"reqd": 1,
		}

	]
}
