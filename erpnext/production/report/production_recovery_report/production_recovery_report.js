// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Production Recovery Report"] = {
	"filters": [
                {
                        "fieldname": "company",
                        "label": ("Company"),
                        "fieldtype": "Link",
                        "options": "Company",
                        "default": frappe.defaults.get_user_default("Company"),
                        "reqd": 1
                },
		 {
                        "fieldname":"from_date",
                        "label": ("From Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "reqd":1
                },
                {
                        "fieldname":"to_date",
                        "label": ("To Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "reqd":1
                },
                {
                        "fieldname": "branch",
                        "label": ("Branch"),
                        "fieldtype": "Link",
                        "options": "Branch",
                        "get_query": function() {
                                var company = frappe.query_report.filters_by_name.company.get_value();
                                return {"doctype": "Branch", "filters": {"company": company, "is_disabled": 0}}
                        },
			"reqd": 1
                },
                {
                        "fieldname": "warehouse",
                        "label": ("Warehouse"),
                        "fieldtype": "Link",
                        "options": "Warehouse",
                        "get_query": function() {
                                var branch = frappe.query_report.filters_by_name.branch.get_value();
                                return {"doctype": "Warehouse", "filters": {"branch": branch}}
                        },
                }
	]
}
