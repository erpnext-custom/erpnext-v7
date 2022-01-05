// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Overall Sales Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": ("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "cost_center",
			"label": ("Parent Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
				var company = frappe.query_report.filters_by_name.company.get_value();
				return {
					'doctype': "Cost Center",
					'filters': [
						['is_disabled', '!=', '1'],
						['company', '=', company],
						['is_group', '=', '1']
					]
				}
			},
			// "on_change": function(query_report) {
			//         var cost_center = query_report.get_values().cost_center;
			//         query_report.filters_by_name.branch.set_input(null);
			//         query_report.filters_by_name.location.set_input(null);
			//         query_report.trigger_refresh();
			//         if (!cost_center) {
			//                 return;
			//         }
			// frappe.call({
			//                 method: "erpnext.custom_utils.get_branch_from_cost_center",
			//                 args: {
			//                         "cost_center": cost_center,
			//                 },
			//                 callback: function(r) {
			//                         query_report.filters_by_name.branch.set_input(r.message)
			//                         query_report.trigger_refresh();
			//                 }
			//         })
			// },
			"reqd": 1,
		},
		// {
		//         "fieldname": "branch",
		//         "label": ("Branch"),
		//         "fieldtype": "Link",
		//         "options": "Branch",
		//         "get_query": function(query_report) {
		//                 var company = frappe.query_report.filters_by_name.company.get_value();
		//                 return {"doctype": "Branch", "filters": {"company": company, "is_disabled": 0}}
		//         }
		// },
		{
			"fieldname": "branch",
			"label": ("Branch"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {
				var cost_center = frappe.query_report.filters_by_name.cost_center.get_value();
				var company = frappe.query_report.filters_by_name.company.get_value();
				if(cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL')
				{
					return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "parent_cost_center": cost_center}}
				}
				else
				{
					return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "is_group": 0}}
				}
			}
		},
		{
			"fieldname": "location",
			"label": ("Location"),
			"fieldtype": "Link",
			"options": "Location",
			"get_query": function() {
				var branch = frappe.query_report.filters_by_name.branch.get_value();
				branch = branch.replace(' - NRDCL','');
				return {"doctype": "Location", "filters": {"branch": branch, "is_disabled": 0}}
			}
		},
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
		{
			"fieldtype": "Break",
		},
		{
			"fieldname": "item_group",
			"label": ("Material Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"get_query": function() {
				return {"doctype": "Item Group", "filters": {"is_group": 0, "is_production_group": 1}}
			},
		},
		{
			"fieldname": "item_sub_group",
			"label": ("Material Sub Group"),
			"fieldtype": "Link",
			"options": "Item Sub Group",
			"get_query": function() {
				var item_group = frappe.query_report.filters_by_name.item_group.get_value();
				return {"doctype": "Item Sub Group", "filters": {"item_group": item_group}}
			}
		},
		{
			"fieldname": "item",
			"label": ("Material"),
			"fieldtype": "Link",
			"options": "Item",
			"get_query": function() {
				var sub_group = frappe.query_report.filters_by_name.item_sub_group.get_value();
				return {"doctype": "Item", "filters": {"item_sub_group": sub_group, "is_production_item": 1}}
			}
		},
		{
			"fieldname": "warehouse",
			"label": ("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"get_query": function() {
				return {"doctype": "Warehouse", "filters": {"disabled": 0}}
			}
		},
		{
			"fieldname": "report_by",
			"label": "Report Base On",
			"fieldtype": "Select",
			"options": ["Sales Order","Delivery Note"],
			"default": "Sales Order",
		},
		{
			"fieldname": "transaction_type",
			"label": ("Transaction Type"),
			"fieldtype": "Select",
			"width": "80",
			"options": ["","Is Allotment", "Is Credit Sale", "Is Rural Sale", "Export", "Is Kidu Sale", "None"],
		},
		{
			"fieldname": "customer",
			"label": ("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"get_query": function() {
				return {"doctype": "Customer", "filters": {"disabled": 0}}
			}
		},
		{
			"fieldname": "customer_group",
			"label": ("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname": "volume",
			"label": ("Volume or Qty"),
			"fieldtype": "Float" 
		},
		{
			"fieldname": "uom",
			"label": ("UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		},
		{
			"fieldname": "aggregate",
			"label": ("Show Aggregate"),
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "summary",
			"label": ("Show Summary"),
			"fieldtype": "Check",
			"default": 0
		},
	]
}
