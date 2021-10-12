// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Tenant Information"] = {
        "filters": [
                {
                        "fieldname": "fiscal_year",
                        "label": __("Fiscal Year"),
                        "fieldtype": "Link",
                        "options": "Fiscal Year",
                        "default": frappe.defaults.get_user_default("fiscal_year"),
                        "reqd": 1,
                },
                {
                        "fieldname": "month",
                        "label": __("Month"),
                        "fieldtype": "Select",
                        "options": ["", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
                        "default": "",
                        "reqd": 1,
                },
                {
                        "fieldname": "dzongkhag",
                        "label": ("Dzongkhag"),
                        "fieldtype": "Link",
                        "width": "100",
                        "options": "Dzongkhags",
                },
                {
                        "fieldname": "location",
                        "label": ("Location"),
                        "fieldtype": "Link",
                        "width": "100",
                        "options": "Locations",
                        "get_query": function () {
                                var dzongkhag = frappe.query_report.filters_by_name.dzongkhag.get_value();
                                return { "doctype": "Locations", "filters": { "dzongkhag": dzongkhag } }
                        }
                },
                {
                        "fieldname": "building_category",
                        "label": ("Building Category"),
                        "fieldtype": "Link",
                        "width": "100",
                        "options": "Building Category"
                },
                {
                        "fieldname": "rental_status",
                        "label": ("Rental Status"),
                        "fieldtype": "Select",
                        "width": "100",
                        "options": [

                                "Allocated", "Surrendered", "Under Maintenance"
                        ]
                },
                {
                        "fieldname": "block_no",
                        "label": ("Block No"),
                        "fieldtype": "Link",
                        "width": "100",
                        "options": "Block No"
                },
                {
                        "fieldname": "building_classification",
                        "label": ("Building Classification"),
                        "fieldtype": "Link",
                        "width": "100",
                        "options": "Building Classification"
                }
        ]
}
