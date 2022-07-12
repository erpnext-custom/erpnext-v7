// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manufacturing Settings', {
	refresh: function(frm) {

	},
	setup: function(frm) {
		frm.set_query("item", "items", function() {
			return {
				filters: {
					'item_group': 'Sales Product',
					'disabled': 0
				}
			};
		})
	} 
});
