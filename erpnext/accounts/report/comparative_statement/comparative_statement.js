// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.require("assets/erpnext/js/financial_statements.js", function() {
	frappe.query_reports["Comparative Statement"] = {
		"filters": [
			{
				"fieldname": "company",
				"label": __("Company"),
				"fieldtype": "Link",
				"options": "Company",
				"default": frappe.defaults.get_user_default("Company"),
				"reqd": 1
			},
			{
				"fieldname": "report",
				"label": __("Report"),
				"fieldtype": "Select",
				"options": ["Comprehensive Income", "Financial Position"],
				"default": "Comprehensive Income",
				"reqd": 1,
			},
			{
				"fieldname": "rep_fy",
				"label": __("Reporting FY"),
				"fieldtype": "Link",
				"options": "Fiscal Year",
				"reqd": 1,
			},
			{
				"fieldname": "com_fy",
				"label": __("Comparision FY"),
				"fieldtype": "Link",
				"options": "Fiscal Year",
				"reqd": 1,
			},
			{
				"fieldtype": "Break",
			},
			{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Select",
				"options": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
				"default": "Jan",
				"reqd": 1,
			},
			{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Select",
				"options": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
				"default": "Dec",
				"reqd": 1,
			},
			{
				"fieldname": "cost_center",
				"label": __("Cost Center"),
				"fieldtype": "Link",
				"options": "Cost Center",
			},
		],
		"formatter": erpnext.financial_statements.formatter,
		"tree": true,
		"name_field": "account",
		"parent_field": "parent_account",
		"initial_depth": 3
	}
});
