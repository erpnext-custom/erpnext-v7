// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Timber Sales Report"] = {
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
			// {
			//         "fieldname": "item_group",
			//         "label": ("Material Group"),
			//         "fieldtype": "Link",
			//         "options": "Item Group",
			//         "get_query": function() {
			//                 return {"doctype": "Item Group", "filters": {"is_group": 0, "is_production_group": 1}}
			//         },
			// },
			{
				"fieldname": "item_group",
				"label": ("Material Group"),
				"fieldtype": "Link",
				"options": "Item Sub Group",
				"get_query": function() {
					return {"doctype": "Item Sub Group", "filters": {"for_report": 1}}
				},
				"on_change": function(){
					var item_group = frappe.query_report.filters_by_name.item_group.get_value();
					frappe.call({
						method:"erpnext.selling.report.timber_sales_report.timber_sales_report.get_item_sub_group",
						args:{"item_group":item_group},
						callback: function(r){
							if(r.message)
							{
								options = []
								for (i = 0; i < r.message.length; i++) { 
									options[i]= r.message[i].name
								}
								console.log(options)
								frappe.query_reports["Timber Sales Report"].filters[8].options = options
								frappe.query_report.filters_by_name.item_sub_group.refresh();
								frappe.query_report.refresh();
							}
						}
						/*	console.log(r.message)
							$.each(r.message, function(i, data){
								$('.input-with-feedback').append(new Option(data.name))
							});
						frappe.query_reports.filters[1].refresh();
						} */
					});
				}
			},
			{
				"fieldname": "item_sub_group",
				"label": ("Material Sub Group"),
				"fieldtype": "Select",
				"options": [],
				// "get_query": function() {
				// 		var item_group = "Timber Products";
				// 		return {"doctype": "Item Sub Group", "filters": {"item_group": item_group}}
				// }
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
				"fieldname": "timber_species",
				"label": ("Timber Species"),
				"fieldtype": "Link",
				"options": "Timber Species",
				"get_query": function() {
					return {"doctype": "Timber Species"}
				}
			},
			{
				"fieldname": "timber_class",
				"label": ("Timber Class"),
				"fieldtype": "Link",
				"options": "Timber Class",
				"get_query": function() {
					return {"doctype": "Timber Class"}
				}
			},
			{
				"fieldname": "timber_type",
				"label":("Timber Type"),
				"fieldtype" : "Select",
				"width" :"80",
				"options": ["All", "Conifer","Broadleaf"],
				"default": "All",
				"reqd" : 1
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
				"default": "Sales Order"
			},
			{
				"fieldname": "transaction_type",
				"label": ("Transaction Type"),
				"fieldtype": "Select",
				"width": "80",
				"options": ["","Is Allotment", "Is Credit Sale", "Is Rural Sale", "Is Export", "Is Kidu Sale", "None"],
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
			{
				"fieldname": "mode",
				"label": ("Report Mode"),
				"fieldtype": "Select",
				"default":"",
				"options":["","Branch and Item Group Wise", "Order Wise"]
			}
	]
}
