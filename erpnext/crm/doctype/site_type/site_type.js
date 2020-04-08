// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Type', {
	onload: function(frm){
		cur_frm.set_query("mode_of_payment",function(){
			return {
				"filters": [
					["credit_allowed", "=", 1]
				]
			}
		});
	},
	refresh: function(frm) {

	},
	payment_required: function(frm){
		cur_frm.toggle_reqd("payment_type", frm.doc.payment_required);
	},
	credit_allowed: function(frm){
		cur_frm.toggle_reqd("mode_of_payment", frm.doc.credit_allowed);
	}
});
