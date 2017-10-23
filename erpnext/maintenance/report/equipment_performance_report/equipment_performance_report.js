// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment Performance Report"] = {
	"filters": [
		{
                                "fieldname": "branch",
                                "label": __("Branch"),
                                "fieldtype": "Link",
                                "options": "Branch",
                        },
		{
				"fieldname": "fy",
				"label": __("Fiscal Year"),
				"fieldtype": "Link",
				"options": "Fiscal Year",
				"reqd": 1,
			},
			{
				"fieldname": "period",
				"label": __("Period"),
				"fieldtype": "Select",
				"options": ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Half Year", "2nd Half Year"],
				"default": "",
			},

	]
}
