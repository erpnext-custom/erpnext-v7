// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Salary Increment"] = {
	"filters": [
	{
                        "fieldname": "uinput",
                        "label": ("Status"),
                        "fieldtype": "Select",
                        "width": "120",
                        "options":["All", "Draft", "Submitted"],
                        "width": "100",
                        "reqd": 1
          },

	{		
			"fieldname":"branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"width": "100"
		}
	]
}
