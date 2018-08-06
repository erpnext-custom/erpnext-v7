// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Employee Asset Report"] = {
	"filters": [
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"on_change": function(query_report) {
				var emp = query_report.get_values().employee;
				if (!emp) {
					return;
				}
				frappe.model.with_doc("Employee", emp, function(r) {
					var fy = frappe.model.get_doc("Employee", emp);
					query_report.filters_by_name.employee_name.set_input(fy.employee_name);
					query_report.trigger_refresh();
				});
			}
		},
		{
			"fieldname": "employee_name",
			"label": __("Employee Name"),
			"fieldtype": "Data",
			"read_only": 1
		},
	],
}
