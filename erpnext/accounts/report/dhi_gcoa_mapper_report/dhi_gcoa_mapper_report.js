// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["DHI GCOA Mapper Report"] = {
	"filters": [
		{
			"fieldname":"map",
			"fieldtype":"Select",
			"options":['Mapped\n','Unmapped'],
			"default":"Mapped"
		},
		{
			"fieldname":"dhi_gcoa_acc",
			"label":"DHI GCOA",
			"fieldtype":"Link",
			"options":"DHI GCOA"
		},
		{
			"fieldname":"is_inter_company",
			"label":"Inter Company",
			"fieldtype":"Select",
			"options":['\n','Inter Company\n','Non Inter Company']
		}
	]
}
