// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Production Progress Report"] = {
	"filters": [
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
						['company', '=', company],
						['is_group', '=', '1']
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
			"fieldname": "uom",
			"label": ("UOM"),
			"fieldtype": "Link",
 			"options": "UOM"
		},
		{
			"fieldtype": "Break"
		},
		{
			"fieldname": "fiscal_year",
			"label": ("Fiscal Year"),
			"fieldtype": "Link",
 			"options": "Fiscal Year",
			"reqd": 1
		},
		{
			"fieldname": "report_period",
			"label": ("Report Period"),
			"fieldtype": "Link",
 			"options": "Report Period",
			"reqd": 1
		},
		{
			"fieldname": "production_group",
			"label": ("Production Group"),
			"fieldtype": "Link",
 			"options": "Production Group",
			"reqd": 1
		},
		{
			"fieldname": "cumulative",
			"label": "Cumulative",
			"fieldtype": "Check",
			"default": 0
		},
		{
                        "fieldname": "display_monthly",
                        "label": "Display Monthly",
                        "fieldtype": "Check",
                        "default": 0
		}
	]
}
