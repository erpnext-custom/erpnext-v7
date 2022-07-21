// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Individual Soelra Report"] = {
	"filters": [
		{
			fieldname: "desuupid",
			fieldtype: "Link",
			options: "Desuup",
			label: "Desuup ID",
			width: 100,
			on_change: function() {
				var desuup = frappe.query_report.filters_by_name.desuupid.get_value()
				frappe.query_report.filters_by_name.dname.set_input(null)
				frappe.query_report.refresh();
				if (!desuup) {
					return;
				}
				frappe.call({
					method: 'frappe.client.get_value',
					args: {
						doctype: 'Desuup',
						filters: {
							'name': desuup
						},
						fieldname: ['desuup_name']
					},
					callback: function(r) {
						frappe.query_report.filters_by_name.dname.set_input(r.message.desuup_name)
						frappe.query_report.refresh()
					}
				})
			}
		},
		{
			fieldname: "dname",
			fieldtype: "Data",
			label: "Name",
			width: 100
		},
		{
			fieldname: "others",
			fieldtype: "Data",
			label: "Others",
			width: 100,
			// on_change: function() {
			// 	frappe.query_report.filters_by_name.desuupid.set_input(null)
			// 	frappe.query_report.filters_by_name.dname.set_input(null)
			// 	frappe.query_report.refresh()
			// }
		}
	]
}
