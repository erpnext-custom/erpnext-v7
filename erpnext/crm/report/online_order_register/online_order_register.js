// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Online Order Register"] = {
	"onload": function (query_report) {
		query_report.filters_by_name.fiscal_year.toggle(false);
	},
	"filters": [
		{
			"fieldname": "report_type",
			"label": "Report Type",
			"fieldtype": "Select",
			"options": ["Register", "Monthly Summary"],
			"reqd": 1,
			"default": "Register",
			"on_change": function (query_report) {
				var report_type = query_report.get_values().report_type;
				var fiscal_year_filter = query_report.filters_by_name["fiscal_year"];
				var from_date_filter = query_report.filters_by_name["from_date"];
				var to_date_filter = query_report.filters_by_name["to_date"];
				var branch_select = query_report.filters_by_name["branch"];

				// var dt_filter= frappe.query_report.get_filter("branch");
				// if (frappe.user.has_role(“Role Name”)) {
				// dt_filter.toggle(false);
				// }
				// dt_filter.refresh();

				if (report_type == 'Monthly Summary') {
					fiscal_year_filter.toggle(true);
					from_date_filter.toggle(false);
					to_date_filter.toggle(false);
					branch_select.toggle(false);
					from_date_filter.df.reqd = 0;
					to_date_filter.df.reqd = 0;
					fiscal_year_filter.df.reqd = 1;

				}
				else {
					fiscal_year_filter.toggle(false);
					from_date_filter.toggle(true);
					to_date_filter.toggle(true);
					branch_select.toggle(true);
					fiscal_year_filter.df.reqd = 0;
					from_date_filter.df.reqd = 1;
					to_date_filter.df.reqd = 1;
					//frappe.fiscal_year.on_load.hidden = 1
				}
				query_report.refresh();
				fiscal_year_filter.refresh();
				from_date_filter.refresh();
				to_date_filter.refresh();

			}
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname": "dzongkhag",
			"label": __("Dzongkhag"),
			"fieldtype": "Link",
			"options": "Dzongkhags",
		},
		{
			"fieldname": "branch",
			"label": __("Select Source Branch"),
			"fieldtype": "Link",
			"options": "Branch",

		},


	]
}
