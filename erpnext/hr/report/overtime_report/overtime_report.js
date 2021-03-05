// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
var d = new Date()
frappe.query_reports["Overtime Report"] = {
	"filters": [
		{
                        "fieldname":"employee",
                        "label": __("Employee"),
                        "fieldtype": "Link",
                        "options": "Employee"
                },
                {
                        "fieldname": "from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.month_start()
                },
                {
                        "fieldname": "to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "default": frappe.datetime.month_end()
                },

                {
                        "fieldname":"branch",
                        "label": __("Branch"),
                        "fieldtype": "Link",
                        "options": "Branch"
                },
		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["", "Paid", "Not Paid"],
		}


	]
}
