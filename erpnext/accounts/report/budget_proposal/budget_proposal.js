// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Budget Proposal"] = {
	"filters": [
			{
			"fieldname": "fiscal_year",
                        "label": __("Fiscal Year"),
                        "fieldtype": "Link",
                        "options": "Fiscal Year",
                        "reqd": 1,
			},

	]
}
