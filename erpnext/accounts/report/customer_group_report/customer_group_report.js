// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Group Report"] = {
	"filters": [
			{
<<<<<<< HEAD
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"default": frappe.defaults.get_user_default("year_start_date"),
			},
			{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"default": frappe.defaults.get_user_default("year_end_date"),
			},
			{
				"fieldname": "branch",
				"label": __("Branch"),
				"fieldtype": "Link",
				"options": "Branch"
			}
=======
                                "fieldname": "from_date",
                                "label": __("From Date"),
                                "fieldtype": "Date",
                                "default": frappe.defaults.get_user_default("year_start_date"),
                        },
                        {
                                "fieldname": "to_date",
                                "label": __("To Date"),
                                "fieldtype": "Date",
                                "default": frappe.defaults.get_user_default("year_end_date"),
                        },
                        {
                                "fieldname": "branch",
                                "label": __("Branch"),
                                "fieldtype": "Link",
                                "options": "Branch"
                        }

>>>>>>> 39393d68c198c5c76fc973c2734c32970e80da6a

	]
}
