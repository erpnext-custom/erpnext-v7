// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Equipment Hire Report"] = {
	"filters": [
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Branch",
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": sys_defaults.year_start_date,
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},

		{
			"fieldname": "customer",
			"label": ("Customer"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Customer"
		},

	]
}
