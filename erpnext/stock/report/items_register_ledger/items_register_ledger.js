// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Items Register Ledger"] = {
	"filters": [
		 {
                        "fieldname":"branch",
                        "label": ("Branch"),
                        "fieldtype": "Link",
                        "options" : "Branch"
                },
                {
                        "fieldname":"from_date",
                        "label": ("From Date"),
                        "fieldtype": "Date",
                },
                {
                        "fieldname":"to_date",
                        "label": ("To Date"),
                        "fieldtype": "Date",
                },
                {
                        "fieldname":"option",
                        "label": ("Option"),
                        "fieldtype": "Select",
                        "options" :  ["Detail", "Summarized"],
                        "reqd" : 1
                }

	]
}
