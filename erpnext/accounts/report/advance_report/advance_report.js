// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Advance Report"] = {
	"filters": [
		{
                        "fieldname":"branch",
                        "label": "Branch",
                        "fieldtype": "Link",
                        "options" : "Branch",
			"reqd": 1
                },
                {
                        "fieldname":"from_date",
                        "label": "From Date",
                        "fieldtype": "Date",
                },
                {
                        "fieldname":"to_date",
                        "label": "To Date",
                        "fieldtype": "Date",
                },
		{
			"fieldtype": "Break"
		},
		{
                        "fieldname":"party_type",
                        "label": "Party Type",
                        "fieldtype": "Select",
                        "options" : ["Supplier", "Customer"],
			"on_change": function(query_report) {
				var party_type = query_report.get_values().party_type;
				if (!party_type) {
					query_report.filters_by_name.party.set_input(null);
					query_report.filters_by_name.advance_on.set_input(null);
					query_report.filters_by_name.item.set_input(null);
				}
				if (party_type == "Supplier") {
					query_report.filters_by_name.party.set_input(null);
					query_report.filters_by_name.item.set_input(null);
					query_report.filters_by_name.advance_on.set_input("Purchase Order");
				}
				else {
					query_report.filters_by_name.party.set_input(null);
					query_report.filters_by_name.item.set_input(null);
					query_report.filters_by_name.advance_on.set_input("Sales Order");
				}
				query_report.trigger_refresh();
			},
			"reqd": 1
                },
		{
                        "fieldname":"party",
                        "label": "Party",
                        "fieldtype": "Dynamic Link",
			"get_options": function() {
				var party_type = frappe.query_report.filters_by_name.party_type.get_value();
				return party_type;
			}
                },
		{
                        "fieldname":"advance_on",
                        "label": "Advance On",
                        "fieldtype": "Select",
                        "options" : ["Sales Order", "Purchase Order"],
			"read_only": 1
                },
		{
                        "fieldname":"item",
                        "label": "Particular",
                        "fieldtype": "Dynamic Link",
			"get_options": function() {
				var party_type = frappe.query_report.filters_by_name.advance_on.get_value();
				return party_type;
			},
			"get_query": function() {
				var branch = frappe.query_report.filters_by_name.branch.get_value();
				var party_type = frappe.query_report.filters_by_name.advance_on.get_value();
				if(branch) {
					return {"doctype": party_type, "filters": {"branch": branch, "docstatus": 1}}
				}
				else {
					return {"doctype": party_type, "filters": {"docstatus": "100"}}
				}
			}
                },
	]
}


