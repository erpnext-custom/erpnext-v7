// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Selling Price', {
	setup: function(frm){
		frm.get_field('item_rates').grid.editable_fields = [
			{fieldname: 'price_based_on', columns: 1},
			{fieldname: 'particular', columns: 3},
			{fieldname: 'selling_price', columns: 2},
			{fieldname: 'location', columns:2},
		]
	},
	refresh: function(frm) {

	}
});
