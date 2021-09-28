// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Consolidation Report"] = {
	"filters": [
		{
			"fieldname":"is_inter_company",
			"label":__("Is Inter Company"),
			"fieldtype":"Select",
			"options":['','Yes','No']
		},
	]
}
