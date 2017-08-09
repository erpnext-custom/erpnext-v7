// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('HR Accounts Settings', {
	refresh: function(frm) {

	}
});



cur_frm.fields_dict['leave_encashment_account'].get_query = function(doc, dt, dn) {
       return {
               filters:{
			"is_group": 0,
			"freeze_account": 0
		}
       }
}
