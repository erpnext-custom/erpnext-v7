// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Timber Allotment To AWBI"] = {
	"filters": [
		{
                        "fieldname":"branch",
                        "label": ("Branch"),
                        "fieldtype": "Link",
                        "options" : "Branch",
                },
                {
                        "fieldname":"customer",
                        "label": ("Firm Name"),
                        "fieldtype": "Link",
                        "options" : "Customer",
                        "get_query": function() {
                                return {"doctype": "Customer", "filters": {"customer_group": "AWBI"}}
                        }
                },
                {
                        "fieldname": "from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        // "default": frappe.defaults.get_user_default("year_start_date"),
                        //"reqd": 1,
                },
                {
                        "fieldname": "to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        // "default": frappe.defaults.get_user_default("year_end_date"),
                       // "reqd": 1,
                },


	]
}
