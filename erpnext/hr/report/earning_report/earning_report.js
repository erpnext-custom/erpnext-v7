// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Earning Report"] = {
	"filters": [
		{
		"fieldtype" :"branch",
		"label" :("Branch"),
		"fieldtype" : "Link",
		"options" : "Branch"
		},
		{
		"fieldname":"from_date",
		"label": __("From Date"),
		"fieldtype": "Select",
		"options": "\nJan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
	},
	{
		"fieldname":"from_date",
		"label": __("From Date"),
		"fieldtype": "Select",
		"options": "\nJan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",

	},
	{
		"fieldname":"fiscal_year",
		"label": __("Fiscal Year"),
		"fieldtype": "Link",
		"options": "Fiscal Year",
	
	},

	]
}
