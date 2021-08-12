// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["EME Bill Report"] = {
	"filters": [
		{
			"fieldname":"name",
			"label":__("Reference"),
			"fieldtype":"Link",
			"options":"EME Payment",
			"reqd":1
		},
		
	]
}
