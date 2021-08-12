// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Consolidation Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label":__("From Date"),
			"fieldtype":"Date",
			"reqd":1,
			"default":frappe.datetime.month_start()
		},
		{
			"fieldname":"to_date",
			"label":__("To Date"),
			"fieldtype":"Date",
			"reqd":1,
			"default":frappe.datetime.month_end()
		},
		{
			"fieldname":"is_inter_company",
			"label":__("Is Inter Company"),
			"fieldtype":"Select",
			"options":['','Yes','No']
		}
	]
}
