// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Advance', {
	refresh: function(frm) {
		if(frm.doc.customer){
			fetch_customer_details(frm);
		}
		
		if(frappe.model.can_read("Project")) {
			frm.add_custom_button(__("Project"), function() {
				frappe.route_options = {"name": frm.doc.project}
				frappe.set_route("Form", "Project", frm.doc.project);
			}, __("View"), true);
		}
	},
	customer: function(frm){
		fetch_customer_details(frm);
	}	
});

var fetch_customer_details = function(frm){
	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Customer",
			filters: {
				name: frm.doc.customer
			},
			fieldname:["customer_details","default_currency"]
		},
		callback: function(r){
			cur_frm.set_value("customer_details", r.message.customer_details);
			cur_frm.set_value("customer_currency", r.message.default_currency);
		}
	});
}