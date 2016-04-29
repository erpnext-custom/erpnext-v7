// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.require("assets/erpnext/js/financial_statements.js");

frappe.query_reports["Statement of Comprehensive Income"] = erpnext.financial_statements;

frappe.query_reports["Statement of Comprehensive Income"]["filters"].push(
	//Custom filter to query based on "Cost Center"
	{
		"fieldname": "cost_center",
		"label": __("Cost Center"),
		"fieldtype": "Link",
		"options": "Cost Center",
	},
	{
	"fieldname": "accumulated_values",
	"label": __("Accumulated Values"),
	"fieldtype": "Check"
})
