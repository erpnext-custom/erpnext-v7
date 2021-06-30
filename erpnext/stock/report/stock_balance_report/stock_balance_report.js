// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Balance Report"] = {
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
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": sys_defaults.year_start_date,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "item_code",
			"label": __("Material Code"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
		},
		{
            "fieldname": "cost_center",
            "label": __("Parent Cost Center"),
			"fieldtype": "Link",
            "width": "80",
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
			"on_change": function(){
				var cost_center = frappe.query_report.filters_by_name.cost_center.get_value();
				// frappe.msgprint(branch)
				frappe.call({
					method:"erpnext.stock.report.stock_balance_report.stock_balance_report.get_warehouse",
					args:{"cost_center":cost_center},
					callback: function(r){
						// console.log(r.message)
						// frappe.query_report.filters_by_name.warehouse.set_option(r.message)					
						if(r.message)
						{
							options = []
							for (i = 0; i < r.message.length; i++) { 
								options[i]= r.message[i].name
							}
							console.log(options)
							frappe.query_reports["Stock Balance Report"].filters[6].options = options
							frappe.query_report.filters_by_name.warehouse.refresh();
							frappe.query_report.refresh();
                                                        // **I have set options dynamically to the below select fieldtype but I need to refresh that field to show that new options.**
							// console.log(frappe.query_reports["Stock Balance Report"].filters[4].options)
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
			},
			"on_change": function(){
				var branch = frappe.query_report.filters_by_name.branch.get_value();
				// frappe.msgprint(branch)
				frappe.call({
					method:"erpnext.stock.report.stock_balance_report.stock_balance_report.get_warehouse",
					args:{"cost_center":branch},
					callback: function(r){
						// console.log(r.message)
						// frappe.query_report.filters_by_name.warehouse.set_option(r.message)					
						if(r.message)
						{
							options = []
							for (i = 0; i < r.message.length; i++) { 
								options[i]= r.message[i].name
							}
							console.log(options)
							frappe.query_reports["Stock Balance Report"].filters[6].options = options
							frappe.query_report.filters_by_name.warehouse.refresh();
							frappe.query_report.refresh();
                                                        // **I have set options dynamically to the below select fieldtype but I need to refresh that field to show that new options.**
							// console.log(frappe.query_reports["Stock Balance Report"].filters[4].options)
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
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Select",
			"width": "80",
			"options":[],
			// "get_query": function(){
			// 	var cost_center = frappe.query_report.filters_by_name.cost_center.get_value();
			// 	// frappe.msgprint(branch)
			// 	frappe.call({
			// 		method:"erpnext.stock.report.stock_balance_report.stock_balance_report.get_warehouse",
			// 		args:{"cost_center":cost_center},
			// 		callback: function(r){
			// 			console.log(r.message)
			// 			// frappe.query_report.filters_by_name.warehouse.set_option(r.message)					
			// 			if(r.message)
			// 			{
			// 				options = []
			// 				for (i = 0; i < r.message.length; i++) { 
			// 					options[i]= r.message[i]
			// 				}
			// 				frappe.query_reports["Stock Balance Report"].filters[4].options = options
			// 				frappe.query_report.trigger_refresh();
            //                                             // **I have set options dynamically to the below select fieldtype but I need to refresh that field to show that new options.**
			// 				// console.log(frappe.query_reports["Stock Balance Report"].filters[4].options)
			// 			}
			// 		}
			// 		/*	console.log(r.message)
			// 			$.each(r.message, function(i, data){
			// 				$('.input-with-feedback').append(new Option(data.name))
			// 			});
			// 		frappe.query_reports.filters[1].refresh();
			// 		} */
			// 	});
			// }
		},
		// {
		// 	"fieldname": "warehouse",
		// 	"label": __("Warehouse"),
		// 	"fieldtype": "Link",
		// 	"width": "80",
		// 	"options": "Warehouse",
		// 	"get_query":function(){
		// 		var cost_center = frappe.query_report.filters_by_name.cost_center.get_value();
		// 		return{"method":"erpnext.stock.report.stock_balance_report.stock_balance_report.get_warehouse",args:{"cost_center":cost_center}}
		// 	} 
		// },
		{
			"fieldname": "item_group",
			"label": __("Material Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Group"
		},
		{
			"fieldname": "item_sub_group",
			"label": __("Material Sub Group"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item Sub Group",
			"get_query":function(){
						var item_group = frappe.query_report.filters_by_name.item_group.get_value();
						return {
							'doctype': "Item Sub Group",
							'filters': [
									['item_group', '=', item_group],
							]
					}
					} 
		},
		{
			"fieldname": "timber_prod_group",
			"label": ("Timber Product Group"),
			"fieldtype": "Link",
			"options": "Item Sub Group",
			"get_query": function() {
					return {"doctype": "Item Sub Group", "filters": {"for_report": 1}}
			},
			"on_change": function(){
				var item_group = frappe.query_report.filters_by_name.timber_prod_group.get_value();
				// frappe.msgprint(branch)
				frappe.call({
					method:"erpnext.selling.report.timber_sales_report.timber_sales_report.get_item_sub_group",
					args:{"item_group":item_group},
					callback: function(r){
						// console.log(r.message)
						// frappe.query_report.filters_by_name.warehouse.set_option(r.message)					
						if(r.message)
						{
							options = []
							for (i = 0; i < r.message.length; i++) { 
								options[i]= r.message[i].name
							}
							console.log(options)
							frappe.query_reports["Stock Balance Report"].filters[10].options = options
							frappe.query_report.filters_by_name.tp_sub_group.refresh();
							frappe.query_report.refresh();
						}
					}
				});
			}
		},
		{
			"fieldname": "tp_sub_group",
			"label": ("Timber Product Sub Group"),
			"fieldtype": "Select",
			"options": [],
			// "get_query": function() {
			// 		var item_group = "Timber Products";
			// 		return {"doctype": "Item Sub Group", "filters": {"item_group": item_group}}
			// }
		},
		{
			"fieldname":"timber_class",
			"label": __("Timber Class"),
			"fieldtype": "Link",
			"options": "Timber Class"
		},
		{
			"fieldname": "uom",
			"label": ("UOM"),
			"fieldtype": "Link",
			"options": "UOM"
		},
	]
}
