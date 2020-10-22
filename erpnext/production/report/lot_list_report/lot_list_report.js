// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Lot List Report"] = {
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
			"label": ("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd" : 1
		},
		{
			"fieldname":"to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd" : 1
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
							frappe.query_reports["Lot List Report"].filters[5].options = options
							frappe.query_report.filters_by_name.warehouse.refresh();
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
			},
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
				if(cost_center != 'Natural Resource Development Corporation Ltd - NRDCL')
				{
						console.log(cost_center)
						return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0, "is_group": 0, "parent_cost_center": cost_center}}
				}
				else
				{
						return {"doctype": "Cost Center", "filters": {"company": company, "is_disabled": 0}}
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
						frappe.query_reports["Lot List Report"].filters[5].options = options
						frappe.query_report.filters_by_name.warehouse.refresh();
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
		},
	},
		// {
		// 	"fieldname": "branch",
		// 	"label": __("Branch"),
		// 	"fieldtype": "Link",
		// 	"options": "Branch",
		// },
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Select",
			"options": [],
		},
		{
			"fieldname": "item_group",
			"label": __("Material Group"),
			"fieldtype": "Link",
			"options": "Item Group",
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
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname": "status",
			"label": ("Status"),
			"fieldtype": "Select",
			"options":["Sold","Taken For Sawing","Stock Transferred","Unsold"]
		}
	]
}
