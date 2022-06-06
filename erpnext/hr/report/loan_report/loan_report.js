// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Loan Report"] = {
	"filters": [
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
			"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", 
				"Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		},
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": sys_defaults.fiscal_year,
		},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
                        "fieldname":"bank",
                        "label": __("Bank"),
                        "fieldtype": "Link",
                        "options": "Financial Institution"
                },
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "parent_cost_center",
			"label": ("Parent Cost Center"),
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
			//         var cost_center = query_report.get_values().cost_center;
			//         query_report.filters_by_name.branch.set_input(null);
			//         query_report.filters_by_name.location.set_input(null);
			//         query_report.trigger_refresh();
			//         if (!cost_center) {
			//                 return;
			//         }
			// frappe.call({
			//                 method: "erpnext.custom_utils.get_branch_from_cost_center",
			//                 args: {
			//                         "cost_center": cost_center,
			//                 },
			//                 callback: function(r) {
			//                         query_report.filters_by_name.branch.set_input(r.message)
			//                         query_report.trigger_refresh();
			//                 }
			//         })
			// },
			"reqd": 1,
		},
		{
			"fieldname": "cost_center",
			"label": ("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
				var parent_cost_center = frappe.query_report.filters_by_name.parent_cost_center.get_value();
				var company = frappe.query_report.filters_by_name.company.get_value();
				if(parent_cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL' && parent_cost_center)
				{
					return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "parent_cost_center": parent_cost_center}}
				}
				else
				{
					return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "is_group": 0}}
				}
			}
		},
	]
}
