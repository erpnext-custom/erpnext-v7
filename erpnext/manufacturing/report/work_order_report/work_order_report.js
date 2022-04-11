// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Work Order Report"] = {
	"filters": [
		{
			"fieldname": "report_type",
			"label": "Report Type",
			"fieldtype": "Select",
			"options": ["In_Progress", "Completed"],
			"reqd": 1,
			"default": "In_Progress",
			"on_change": function (query_report) {
				var report_type = query_report.get_values().report_type;
				var from_date_filter = query_report.filters_by_name["from_date"];
				var to_date_filter = query_report.filters_by_name["to_date"];

				if (report_type == 'Completed') {
					from_date_filter.toggle(false);
					to_date_filter.toggle(false);
					from_date_filter.df.reqd = 0;
					to_date_filter.df.reqd = 0;
				}
				else {
					from_date_filter.toggle(true);
					to_date_filter.toggle(true);
					from_date_filter.df.reqd = 1;
					to_date_filter.df.reqd = 1;
				}
				query_report.refresh();
				from_date_filter.refresh();
				to_date_filter.refresh();

			}
		},
		{
			"fieldname":"from_date",
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1
		},
		{
			"fieldname": "cost_center",
			"label": ("Parent Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
				return {
					'doctype': "Cost Center",
					'filters': [
						['is_disabled', '!=', '1'],
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
		},
		{
		"fieldname": "branch",
		"label": ("Branch"),
		"fieldtype": "Link",
		"options": "Cost Center",
		"get_query": function() {
			var cost_center = frappe.query_report.filters_by_name.cost_center.get_value();
			// var company = frappe.query_report.filters_by_name.company.get_value();
			if(cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL')
			{
				return {"doctype": "Cost Center", "filters": {"is_disabled": 0, "parent_cost_center": cost_center}}
			}
			else
			{
				return {"doctype": "Cost Center", "filters": {"is_disabled": 0, "is_group": 0}}
			}
		}
	},
	{
		"fieldname": "item",
		"label": ("Item"),
		"fieldtype": "Link",
		"options": "Item",
		"get_query": function() {
			return {
				'doctype': "Item",
				'filters': [
					['disabled', '!=', '1'],
				]
			}
		},
	}
	]
}
