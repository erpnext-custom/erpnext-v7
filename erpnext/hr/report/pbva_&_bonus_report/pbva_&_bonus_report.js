// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["PBVA & Bonus Report"] = {
	"filters": [
		{
			"fieldname":"fiscal_year",
			"label": __("Fiscal Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": sys_defaults.fiscal_year,
		},
		{
			"fieldname":"type",
			"label": __("Type"),
			"fieldtype": "Select",
			"options": ["Bonus","PBVA"],
			"reqd": 1
		},
		{
            "fieldname": "cost_center",
            "label": __("Parent Cost Center"),
			"fieldtype": "Link",
            "width": "80",
			"options": "Cost Center",
			"get_query": function() {
				return {
						'doctype': "Cost Center",
						'filters': [
								['is_disabled', '!=', '1'],
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
					if (frappe.query_report.filters_by_name.cost_center.get_value())
					{
						var cost_center = frappe.query_report.filters_by_name.cost_center.get_value();
						if(cost_center!= 'Natural Resource Development Corporation Ltd - NRDCL')
						{
								return {"doctype": "Cost Center", "filters": {"is_disabled": 0, "parent_cost_center": cost_center}}
						}
						else
						{
								return {"doctype": "Cost Center", "filters": {"is_disabled": 0, "is_group": 0}}
						}
					}
					else
					{
						return {"doctype": "Cost Center", "filters": {"is_disabled": 0, "is_group": 0}}
					}

					
		}
	},
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"on_change": function(query_report) {
				var emp = query_report.get_values().employee;
				if (!emp) {
					return;
				}
				frappe.model.with_doc("Employee", emp, function(r) {
					var fy = frappe.model.get_doc("Employee", emp);
					query_report.filters_by_name.e_name.set_input(fy.employee_name);
					query_report.filters_by_name.cid.set_input(fy.passport_number);
					query_report.filters_by_name.tpn.set_input(fy.tpn_number);
					query_report.trigger_refresh();
				});
			}
		},
		{
			"fieldname":"e_name",
			"fieldtype":"Data",
			"label": __("Employee Name"),
			"read_only": 1
		},
		{
			"fieldname":"cid",
			"fieldtype":"Data",
			"label": __("CID"),
			"read_only": 1
		},
		{
			"fieldname":"tpn",
			"fieldtype":"Data",
			"label": __("TPN"),
			"read_only": 1
		},
	]
}
