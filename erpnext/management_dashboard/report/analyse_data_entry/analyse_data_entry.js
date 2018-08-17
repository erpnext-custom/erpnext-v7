// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Analyse Data Entry"] = {
	"filters": [
		{
                                "fieldname": "branch",
                                "label": __("Branch"),
                                "fieldtype": "Link",
                                "options": "Branch",
              	},
		{
                        	"fieldname": "transaction",
                        	"label": ("Transaction"),
                        	"fieldtype": "Select",
                        	"width": "80",
                        	"options": ["", "Break Down Report","Job Card", "Equipment Hiring Form", "Material Issue", "Material Transfer", "Material Receipt","Purchase Order", "Journal Entry","Payment Entry", "Direct Payment"]

                },
		{
                                "fieldname": "from_date",
                                "label": __("From Date"),
                                "fieldtype": "Date",
                                "default": frappe.datetime.month_start(frappe.datetime.get_today()),
              },
	      {
                                "fieldname": "to_date",
                                "label": __("To Date"),
                                "fieldtype": "Date",
                                "default": frappe.datetime.month_end(frappe.datetime.get_today()),
              },

	]
}
