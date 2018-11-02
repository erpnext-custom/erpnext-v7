// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Inter Company Transaction Report"] = {
	"filters": [
		{
			"fieldname":"party",
			"label": __("Party"),
			"fieldtype": "Select",
			"required": 1,
			"options":['',]			
		},
		{
			"fieldname":"start_date",
			"label": ("Start Date"),
			"fieldtype": "Date",
			"width": "60",
			"required":1,
			"default": sys_defaults.year_start_date,
		},
		{
			"fieldname":"end_date",
			"label": ("End Date"),
			"fieldtype": "Date",
			"width": "60",
			"required":1,
			"default": frappe.datetime.get_today(),
		},
		{
			"fieldname": "branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"width": "60",
			"options": "Branch",
		},
	],
	onload: function(report) {
            select = $('div[data-fieldname="party"]').children()
            frappe.call({
                    method: "erpnext.accounts.general_ledger.get_inter_parties",                       
                    callback: function(r) {
                    	console.log(r.message);
                            $.each(r.message, function(i, j) {
                            	console.log("i: " + i); console.log("j: "+j);
                                    select.append($('<option>', {value: j, text: j}))
                            })
                    }
            })
    	}
}
