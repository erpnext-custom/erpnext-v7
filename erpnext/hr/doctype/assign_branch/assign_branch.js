// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "user_id", "user")
cur_frm.add_fetch("employee", "branch", "current_branch")

frappe.ui.form.on('Assign Branch', {
	refresh: function(frm) {

	}
});
