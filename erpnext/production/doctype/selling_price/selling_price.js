// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Selling Price', {
	setup: function(frm) {
		frm.get_field('item_rates').grid.editable_fields = [
			{fieldname: 'price_based_on', columns: 3},
			{fieldname: 'particular', columns: 3},
			{fieldname: 'selling_price', columns: 3},
			{fieldname: 'item_sub_group', columns:3},
		]
		frm.clear_table("item_branch");
	}
});
frappe.ui.form.on('Selling Price Branch', {
	item_branch_add: function(frm, cdt,cdn){
		frappe.model.set_value(cdt, cdn, "branch", null);
		cur_frm.refresh_field()
	}
});
