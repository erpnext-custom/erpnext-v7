// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Operators Overtime Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.year_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": get_today()
		},
		{
			"fieldname":"cost_center",
			"label": __("Cost Center"),
			"fieldtype": "Link",
			"options": "Cost Center",
			"get_query": function() {return {'filters': [['Cost Center', 'is_disabled', '!=', '1']]}}
		},
		{
			"fieldname":"operator",
			"label": __("Operator"),
			"fieldtype": "Select",
			"options": ['',]
		},
	],
	
	onload: function(report){
		select = $('div[data-fieldname="operator"]').children();
		frappe.call({
			method: "erpnext.hr.report.operators_overtime_report.operators_overtime_report.get_operators",
			callback: function(r) {
				console.log(r.message);
				$.each(r.message, function(i,j){
					console.log("id: " + j[0]); console.log("name: "+j[1]);
					select.append($('<option>', {value: j[0], text:j[1]}));
				});
			}
		});	
	}
}
