// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Progress Graphs"] = {
	"filters": [
		{
                        "fieldname": "project",
                        "label": ("Gyalsung Academy"),
                        "fieldtype": "Link",
                        "options": "Project",
                        "get_query": function() {
                                        return {
                                                        'doctype': "Project",
                                                        'filters': [
                                                                        ['is_group', '=', '1']
                                                        ]
                                        }
                        },
                },
                {
                        "fieldname": "activity",
                        "label": ("Activity"),
                        "fieldtype": "Link",
                        "options": "Project",
                        "get_query": function() {
                                        var parent_project = frappe.query_report.filters_by_name.project.get_value();
                                        return { 'doctype': "Project",
                                                'filters': [
                                                        ['is_group', '=', '0'],
                                                        ['parent_project', '=', parent_project]
                                ]
                        }
                }
		},
                {
                        fieldname: "from_date",
                        label: __("From Date"),
                        fieldtype: "Date",
                        default: frappe.defaults.get_user_default("year_start_date"),
                        reqd: 0
                },
                {
                        fieldname:"to_date",
                        label: __("To Date"),
                        fieldtype: "Date",
                        default: frappe.defaults.get_user_default("year_end_date"),
                        reqd: 0
                },
                {
                        fieldname: "range",
                        label: __("Range"),
                        fieldtype: "Select",
                        options: [
				{ "value": "Monthly", "label": __("Monthly") }
                        ],
                        default: "Monthly",
                        reqd: 0
                }
]
}
