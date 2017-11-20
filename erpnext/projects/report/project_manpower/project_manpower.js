// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.provide("erpnext.financial_statements");

frappe.require("assets/erpnext/js/project_statements.js", function() {
frappe.query_reports["Project Manpower"] = {
	"filters": [
		{
			"fieldname": 	"project",
			"label": 		("Project"),
			"fieldtype": 	"Link",
			"options":		"Project",
			"reqd": 1,
			"width": "200"
		}
	],
	"formatter": function(row, cell, value, columnDef, dataContext, default_formatter){
		if (columnDef.df.fieldname=="project_id"){
			value = dataContext.project_name;
			
			columnDef.df.link_onclick = 
				"erpnext.project_statements.open_documents(" + JSON.stringify(dataContext) + ")";
		}
		
		value = default_formatter(row, cell, value, columnDef, dataContext);
		
		return value;
	},
}
});