// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Cash Book"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
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
									   //  query_report.filters_by_name.from_date.set_input(fy.year_start_date);
									   //  query_report.filters_by_name.to_date.set_input(fy.year_end_date);
										 query_report.trigger_refresh();
								 });
						 }
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jul\nAug\nSep\nOct\nNov\nDec\nJan\nFeb\nMar\nApr\nMay\nJun",
			"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
				"Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
			"reqd": 1	
		},
		{
			"fieldname":"account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"get_query": function() {
				var company = frappe.query_report.filters_by_name.company.get_value();
				return {
					"doctype": "Account",
					"filters": {
						"company": company,
						"list_in_filter": 1
					}
				}
			}
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center/Activity"),
			"fieldtype": "Link",
			"options": "Cost Center",
		},
		{
                        "fieldname":"voucher_no",
                        "label": __("Voucher Number"),
                        "fieldtype": "Data",
        },
		{
			"fieldtype": "Break",
		},
		{
			"fieldname":"party_type",
			"label": __("Party Type"),
			"fieldtype": "Select",
			"options": ["", "Customer", "Supplier", "Employee", "Equipment"],
			"default": ""
		},
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var party_type = frappe.query_report.filters_by_name.party_type.get_value();
				var party = frappe.query_report.filters_by_name.party.get_value();
				if(party && !party_type) {
					frappe.throw(__("Please select Party Type first"));
				}
				return party_type;
			}
		},
		 {
                        "fieldname":"business_activity",
                        "label": __("Funding Pool"),
                        "fieldtype": "Link",
                        "options": "Business Activity",
                },

		{
			"fieldname":"group_by_voucher",
			"label": __("Group by Voucher"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname":"group_by_account",
			"label": __("Group by Account"),
			"fieldtype": "Check",
		},
		/*{
			"fieldname":"letter_head",
			"label": __("Letter Head"),
			"fieldtype": "Link",
			"options": "Letter Head",
			"default": frappe.defaults.get_default("letter_head"),
		} */
	]
}
