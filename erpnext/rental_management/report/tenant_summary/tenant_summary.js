// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Tenant Summary"] = {
	"filters": [
		{
			fieldname: "name",
			label: "Tenant Code",
			fieldtype: "Link",
			width: "80",
			options: "Tenant Information",
			on_change: function() {
				var tenant = frappe.query_report.filters_by_name.name.get_value()
				frappe.query_report.filters_by_name.tenantname.set_input(null)
				frappe.query_report.refresh();
				if (!tenant) {
					return;
				}
				frappe.call({
					method: 'frappe.client.get_value',
					args: {
						doctype: 'Tenant Information',
						filters: {
							'name': tenant
						},
						fieldname: ['tenant_name']
					},
					callback: function(r) {
						frappe.query_report.filters_by_name.tenantname.set_input(r.message.tenant_name)
						frappe.query_report.refresh()
					}
				})
			},
			"reqd": 1,
		},
		{
			fieldname: "tenantname",
			label: "Tenant Name",
			fieldtype: "Data",
			width: "80",
			read_only: 1,
		}
	]
}
