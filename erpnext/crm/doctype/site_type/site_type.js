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

		// Following code added by SHIV on 2020/12/30 to accommodate Phase-II
		// Advance payment settings moved to child table
		cur_frm.fields_dict['advances'].grid.get_field('product_group').get_query = function(doc, cdt, cdn){
			var child = locals[cdt][cdn];
			return {
				"query": "erpnext.crm_utils.get_product_groups_query",
				filters: {
					'product_category': child.product_category
				}
			}
		};
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

// Following code added by SHIV on 2020/12/30 to accommodate Phase-II changes
frappe.ui.form.on('Site Type Advance', {
	product_category: function(frm, cdt, cdn){
		var row = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "product_group", null);
	},
});