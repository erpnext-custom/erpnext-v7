// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Royalty Payment Report"] = {
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
			}
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_start_date")
		},
		{
			"fieldname": "to_date",
			"label": ("To Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_user_default("year_end_date")
		},
		{
			"fieldtype":"Break"
		},
		{
			"fieldname": "workflow_state",
			"label": ("Workflow State"),
			"fieldtype": "Select",
			"options":["","Approved","Draft","Rejected", "Rejected by Supervisor", "Waiting Approval", "Waiting Supervisor Approval"]
		},
		{
			"fieldname": "payment_state",
			"label": ("Payment State"),
			"fieldtype": "Select",
			"options":["","Paid","Due","None"]
		},
		{
			"fieldname": "detail",
			"label": ("Show in Detail"),
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "range",
			"label": ("Range"),
			"fieldtype": "Link",
			"options": "Range"
		},
		{
			"fieldname": "item_sub_group",
			"label": ("Material Sub Group"),
			"fieldtype": "Link",
			"options": "Item Sub Group"
		},
		{
			"fieldtype":"Break"
		},
		{
			"fieldname": "timber_class",
			"label": ("Timber Class"),
			"fieldtype": "Link",
			"options": "Timber Class"
		},
		{
			"fieldname": "ref_id",
			"label": ("Royalty Ref ID"),
			"fieldtype": "Link",
			"options": "Royalty Payment"
		},
		{
			"fieldname": "payment_id",
			"label": ("Payment Ref ID"),
			"fieldtype": "Link",
			"options": "Journal Entry"
		},
		{
			"fieldname": "quantity",
			"label": ("Quantity"),
			"fieldtype": "Float"
		},
		{
			"fieldname": "rate",
			"label": ("Royalty Rate"),
			"fieldtype": "Float"
		}
		


	]
}
