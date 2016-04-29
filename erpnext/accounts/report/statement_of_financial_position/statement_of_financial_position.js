// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.require("assets/erpnext/js/financial_statements.js");

frappe.query_reports["Statement of Financial Position"] = erpnext.financial_statements;

frappe.query_reports["Statement of Financial Position"]["filters"].push({
	"fieldname": "cost_center",
	"label": __("Cost Center"),
	"fieldtype": "Link",
	"options": "Cost Center",
})
