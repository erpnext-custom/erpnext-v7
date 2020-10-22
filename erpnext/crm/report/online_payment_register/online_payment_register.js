// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Online Payment Register"] = {
	onload: function (query_report) {
		query_report.filters_by_name.fiscal_year.toggle();
	},
	"filters": [
		{
			"fieldname": "report_type",
			"label": "Report Type",
			"fieldtype": "Select",
			"options": ["Register", "Monthly Summary"],
			"default": "Register",
			"reqd": 1,
			"on_load": function (query_report) {
				console.log('on_load');
				query_report.filters_by_name["fiscal_year"].df.hidden = 1
			},
			"on_change": function (query_report) {
				console.log(query_report)
				var report_type = query_report.get_values().report_type;
				var fiscal_year_filter = query_report.filters_by_name["fiscal_year"];
				var from_date_filter = query_report.filters_by_name["from_date"];
				var to_date_filter = query_report.filters_by_name["to_date"];
				var status_filter = query_report.filters_by_name["status"];

				if (report_type == 'Monthly Summary') {
					console.log(query_report)
					fiscal_year_filter.toggle(true);
					from_date_filter.toggle(false)
					to_date_filter.toggle(false)
					status_filter.toggle(false)
					from_date_filter.df.reqd = 0
					to_date_filter.df.reqd = 0
					fiscal_year_filter.df.reqd = 1
				}
				else {
					fiscal_year_filter.toggle(false)
					from_date_filter.toggle(true)
					to_date_filter.toggle(true)
					status_filter.toggle(true)
					fiscal_year_filter.df.reqd = 0
					from_date_filter.df.reqd = 1
					to_date_filter.df.reqd = 1
				}
				query_report.refresh();
				fiscal_year_filter.refresh();
				from_date_filter.refresh()
				to_date_filter.refresh()
				status_filter.refresh()
			}
		},
		{
			"fieldname": "fiscal_year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
		},
		{
			"fieldname": "from_date",
			"label": ("From Date"),
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
			"fieldname": "dzongkhag",
			"label": __("Dzongkhag"),
			"fieldtype": "Link",
			"options": "Dzongkhags",
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"default": "Successful",
			"options": ["All", "Failed", "Pending", "Successful", "Cancelled"],
		},
	]
}
