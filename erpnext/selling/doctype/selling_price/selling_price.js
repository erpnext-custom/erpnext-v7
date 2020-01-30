// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center");
frappe.ui.form.on('Selling Price', {
	setup: function(frm) {
		frm.get_field('item_rates').grid.editable_fields = [
//			{fieldname: 'price_based_on', columns: 3},
			{fieldname: 'particular', columns: 3},
			{fieldname: 'selling_price', columns: 3},
//			{fieldname: 'item_sub_group', columns:3},
		]
	},

	refresh: function(frm) {

	}
});
