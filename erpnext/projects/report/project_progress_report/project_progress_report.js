// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Project Progress Report"] = {
	"filters": [
		/*{
                        "fieldname": "company",
                        "label": ("Company"),
                        "fieldtype": "Select",
			"options": "GYALSUNG INFRA - GYALSUNG",
			"default": "GYALSUNG INFRA - GYALSUNG",
                        "reqd": 1
                },*/
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

                /*{
                        "fieldname": "cost_center",
                        "label": ("Parent Branch"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "get_query": function() {
                                        var company = frappe.query_report.filters_by_name.company.get_value();
                                        return {
                                                        'doctype': "Cost Center",
                                                        'filters': [
                                                                        ['is_disabled', '!=', '1'],
                                                                        ['parent_cost_center', '=', company],
                                                                        ['is_group', '=', '1']
                                                        ]
                                        }
                        },
                },
		{
                        "fieldname": "branch",
                        "label": ("Branch"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "get_query": function() {
                                        var cost_center = frappe.query_report.filters_by_name.cost_center.get_value();
                                        var company = frappe.query_report.filters_by_name.company.get_value();
					return { 'doctype': "Cost Center",
						'filters': [
							['is_disabled', '!=', '1'],
							['parent_cost_center', '=', cost_center]
				]
			}
		}
		},
		{
                        "fieldname": "from_date",
                        "label": __("From Date"),
                        "fieldtype": "Date",
                        "default": frappe.defaults.get_user_default("year_start_date"),
                        "reqd": 1,
                },
                {
                        "fieldname": "to_date",
                        "label": __("To Date"),
                        "fieldtype": "Date",
                        "default": frappe.defaults.get_user_default("year_end_date"),
                        "reqd": 1,
                },*/
		{
                        "fieldname": "status",
                        "label": __("Status"),
                        "fieldtype": "Select",
                        "options": ['', 'Planning', 'Ongoing', 'Completed', 'Cancelled']
                },

		/*{
                        "fieldname": "show_all",
                        "label": __("Show All Activities"),
                        "fieldtype": "Check",
                        "default": 0
                }*/

]}
