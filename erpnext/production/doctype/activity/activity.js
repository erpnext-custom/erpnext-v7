// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Activity', {
	refresh: function(frm) {

	},
	setup: function(frm){
                frm.get_field('items').grid.editable_fields = [
                        {fieldname: 'item', columns: 2},
                        {fieldname: 'item_name', columns: 4},
                        {fieldname: 'item_group', columns: 3},
                        {fieldname: 'item_sub_group', columns: 3}
                ];
        }
});
