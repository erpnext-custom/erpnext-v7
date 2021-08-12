// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Expense and Performance Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.year_start(),
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.get_today(),
			"reqd": 1,
		},
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"reqd": 1,
		},
		{
			"fieldname":"equipment_type",
			"label": __("Equipment Type"),
			"fieldtype": "Link",
			"options": "Equipment Type"
		},
		{
			"fieldname":"equipment",
			"label": __("Equipment"),
			"fieldtype": "Link",
			"options": "Equipment",
			"on_change": function(query_report) {
				var equipment = query_report.get_values().equipment;
				query_report.filters_by_name.equipment_no.set_input(null);
				query_report.trigger_refresh();
				if (!equipment) {
					return;
				}
				frappe.call({
					method: 'frappe.client.get_value',
					args: {
						doctype: 'Equipment',
						filters: {
							'name': equipment
						},
						fieldname: ['equipment_number']
					},

					callback: function(r) {
						query_report.filters_by_name.equipment_no.set_input(r.message.equipment_number)
						query_report.trigger_refresh();
					}
				})
			},
        },
		{
			"fieldname":"equipment_no",
			"label": __("Reg. No"),
			"fieldtype": "Data",
			"read_only": 1,
		},
		{
			"fieldname":"supplier",
			"label": __("Vendor Name"),
			"fieldtype": "Link",
			"options": "Supplier"
        },
		{
			"fieldname":"company_owned",
			"label": __("Company Owned"),
			"fieldtype": "Check",
			"on_change": function(query_report){
				if (query_report.get_values().company_owned){
					query_report.filters_by_name.supplier.set_input(null)
					query_report.trigger_refresh();
				}
			}
		}
	]
}
