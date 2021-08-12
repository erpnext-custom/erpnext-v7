// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Daily EME Working Hour"] = {
	"filters": [
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Data",
			"read_only": 1
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"on_change" : function(query_report) {
				var branch = query_report.get_values().branch;
				query_report.filters_by_name.cost_center.set_input(null);
				query_report.trigger_refresh();
				if ( !branch ){
					return;
				}
				frappe.call({
					method: 'frappe.client.get_value',
					args: {
						doctype: 'Branch',
						filters: { 
							'name': branch
						},
						fieldname: ['cost_center']
					},
					callback: function(r){
						query_report.filters_by_name.cost_center.set_input(r.message.cost_center)
						query_report.trigger_refresh();
					}
				})	
			}
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd" : 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname" : "equipment_type",
			"label": __("Equipment Type"),
			"fieldtype": "Link",
			"options": "Equipment Type"
		},
		{
			"fieldname": "company_owned",
			"label": __("Company Owned"),
			"fieldtype": "Check"
		}
	]
}
