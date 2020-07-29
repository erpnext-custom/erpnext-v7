// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Site Registration Report"] = {
	"filters": [
		/*
		{
			"fieldname":"report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
			"options": "\nSite Wise\nDzongkhag Wise",
			"default": "Site Wise",
			"display": 1
		},*/
                {
                        "fieldname": "dzongkhag",
                        "label": ("Dzongkhag"),
                        "fieldtype": "Link",
                        "options": "Dzongkhags",
                },
                {
                        "fieldname": "from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "reqd": 1,
                },
                {
                        "fieldname": "to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "reqd": 1,
                },
                {
                        "fieldname": "item_sub_group",
                        "label": ("Material"),
                        "fieldtype": "Link",
                        "options": "Item Sub Group",
                        "reqd": 1,
                        "get_query": function() {
                                return {"doctype": "Item Sub Group", "filters": {"is_crm_item": 1}}
                        }
                },
		/*
                {
                        "fieldname": "item",
                        "label": ("Material"),
                        "fieldtype": "Link",
                        "options": "Item",
                        "get_query": function() {
                                var sub_group = frappe.query_report.filters_by_name.item_sub_group.get_value();
                                return {"doctype": "Item", "filters": {"item_sub_group": sub_group}}
                        }
                },*/
	]
}
