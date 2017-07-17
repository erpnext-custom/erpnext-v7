// Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.require("assets/erpnext/js/financial_statements.js", function() {

   frappe.query_reports["Statement of Cash Flow"] = erpnext.financial_statements;

   frappe.query_reports["Statement of Cash Flow"]["filters"].push({
		"fieldname": "cost_center",
		"label": __("Cost Center"),
		"fieldtype": "Link",
		"options": "Cost Center",
		"get_query": function() {return {'filters': [['Cost Center', 'is_disabled', '!=', '1']]}}
	},
	{
		"fieldname": "accumulated_values",
		"label": __("Accumulated Values"),
		"fieldtype": "Check",
   	});
});
