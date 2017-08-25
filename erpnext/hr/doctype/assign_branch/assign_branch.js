// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "user_id", "user")

frappe.ui.form.on('Assign Branch', {
	refresh: function(frm) {

	}
});
