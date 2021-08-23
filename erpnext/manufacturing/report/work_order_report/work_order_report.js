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
		}
	]
}
