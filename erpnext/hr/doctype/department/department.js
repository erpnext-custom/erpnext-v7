// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Department', {
	refresh: function(frm) {
	}
});

cur_frm.fields_dict.cost_center.get_query = function(doc) {
	return{
		filters:{
			'is_group': 0,
			'is_disabled': 0,
		}
	}
}
