// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Salary Increment"] = {
	"filters": [
	{
			"fieldname":"branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100"
		},
		{
			"fieldname" : "uinput",
			"label":("Status"),
			"fieldtype": "Select",
			"width" : "120",
			"options": ["Draft", "Submitted"],
		},
	]
}
