// Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Party Wise Ledger"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"on_change": function(query_report) {
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
					var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
					query_report.filters_by_name.from_date.set_input(fy.year_start_date);
					query_report.filters_by_name.to_date.set_input(fy.year_end_date);
					query_report.trigger_refresh();
				});
			}
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date"),
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date"),
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Select",
			"options": ["Customer", "Supplier", "Employee", "Equipment"],
			"default": "Customer"
		},
		{
			"fieldtype": "Break",
		},
		// {
		// 	"fieldname":"cost_center",
		// 	"label": __("Cost Center"),
		// 	"fieldtype": "Link",
		// 	"options": "Cost Center"
		// },
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
			"fieldname":"accounts",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account"
		},
		{
			"fieldname": "show_zero_values",
			"label": __("Show zero values"),
			"fieldtype": "Check"
		},
		{
			"fieldname":"inter_company",
			"label": __("DHI Inter Company?"),
			"fieldtype": "Check",
		},
		{
			"fieldname":"group_by_party",
			"label": __("Group by party?"),
			"fieldtype": "Check",
		}
	]
}
