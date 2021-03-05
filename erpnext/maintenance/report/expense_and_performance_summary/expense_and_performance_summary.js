// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Expense and Performance Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
		},
		/*{
                        "fieldname":"year",
                        "label": __("Year"),
                        "fieldtype": "Link",
                        "options": "Fiscal Year",
                        "reqd": 1,
			"default": frappe.defaults.get_user_default("fiscal_year"),
                },*/
		{
                        "fieldname":"equipment",
                        "label": __("Equipment"),
                        "fieldtype": "Link",
                        "options": "Equipment",
                        "reqd": 1,
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
	]
}
