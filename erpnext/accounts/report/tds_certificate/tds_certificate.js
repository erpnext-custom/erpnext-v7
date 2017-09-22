// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["TDS Certificate"] = {
	"filters": [
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
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
			"fieldname": "vendor_name",
			"label": __("Vendor Name"),
			"fieldtype": "Link",
			"options": "Supplier",
			"on_change": function(query_report) {
				var vendor = query_report.get_values().vendor_name;
				if (!vendor) {
					return;
				}
				frappe.model.with_doc("Supplier", vendor, function(r) {
					var fy = frappe.model.get_doc("Supplier", vendor);
					query_report.filters_by_name.vendor_tpn_no.set_input(fy.vendor_tpn_no);
					query_report.trigger_refresh();
				});
			}
		},
		{
			"fieldname": "vendor_tpn_no",
			"label": __("Vendor TPN Number"),
			"fieldtype": "Data",
			"read_only": 1
		},
	],
}
