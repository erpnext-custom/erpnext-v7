// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Employee TDS Certificate"] = {
	"filters": [
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
			"options": "Employee",
			"reqd": 1,
			"on_change": function(query_report) {
				var emp = query_report.get_values().employee;
				if (!emp) {
					return;
				}
				frappe.model.with_doc("Employee", emp, function(r) {
					var fy = frappe.model.get_doc("Employee", emp);
					query_report.filters_by_name.e_name.set_input(fy.employee_name);
					query_report.filters_by_name.cid.set_input(fy.passport_number);
					query_report.filters_by_name.tpn.set_input(fy.tpn_number);
					query_report.trigger_refresh();
				});
			}
		},
		{
			"fieldname":"e_name",
			"fieldtype":"Data",
			"label": __("Employee Name"),
			"read_only": 1
		},
		{
			"fieldname":"cid",
			"fieldtype":"Data",
			"label": __("CID"),
			"read_only": 1
		},
		{
			"fieldname":"tpn",
			"fieldtype":"Data",
			"label": __("TPN"),
			"read_only": 1
		},
	]
}
