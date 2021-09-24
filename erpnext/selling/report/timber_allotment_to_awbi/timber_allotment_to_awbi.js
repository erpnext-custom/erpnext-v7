// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Timber Allotment To AWBI"] = {
	"filters": [
		// {
                //         "fieldname":"branch",
                //         "label": ("Branch"),
                //         "fieldtype": "Link",
                //         "options" : "Branch",
                // },
                {
			"fieldname": "company",
			"label": ("Company"),
			"fieldtype": "Link",
 			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
                {
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
                                                ['is_group', '=', '1'],
                                                ['company', '=', company]
                                        ]
                                }
                        },
                        // "on_change": function(query_report) {
                        // 	var cost_center = query_report.get_values().cost_center;
                        // 	query_report.filters_by_name.branch.set_input(null);
                        // 	query_report.trigger_refresh();
                        // 	if (!cost_center) {
                        // 		return;
                        // 	}
                        // 	frappe.call({
                        // 		method: "erpnext.custom_utils.get_branch_from_cost_center",
                        // 		args: {
                        // 			"cost_center": cost_center,
                        // 		},
                        // 		callback: function(r) {
                        // 			query_report.filters_by_name.branch.set_input(r.message)
                        // 			query_report.trigger_refresh();
                        // 		}
                        // 	})
                        // },
                        "reqd": 1,
                },
                {
                        "fieldname": "branch",
                        "label": ("Branch"),
                        "fieldtype": "Link",
                        "options": "Cost Center",
                        "get_query": function() {
                                        var cost_center = frappe.query_report.filters_by_name.cost_center.get_value();
                                        var company = frappe.query_report.filters_by_name.company.get_value();
                                        if(cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL')
                                        {
                                                        return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "parent_cost_center": cost_center}}
                                        }
                                        else
                                        {
                                                        return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "is_group": 0}}
                                        }
                        }
                },
                {
                        "fieldname":"customer",
                        "label": ("Firm Name"),
                        "fieldtype": "Link",
                        "options" : "Customer",
                        "get_query": function() {
                                return {"doctype": "Customer", "filters": {"customer_group": "AWBI"}}
                        }
                }
                // {
                //         "fieldname": "from_date",
                //         "label": __("From Date"),
                //         "fieldtype": "Date",
                //         // "default": frappe.defaults.get_user_default("year_start_date"),
                //         //"reqd": 1,
                // },
                // {
                //         "fieldname": "to_date",
                //         "label": __("To Date"),
                //         "fieldtype": "Date",
                //         // "default": frappe.defaults.get_user_default("year_end_date"),
                //        // "reqd": 1,
                // }


	]
}
//test