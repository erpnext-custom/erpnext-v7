// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("location", "branch", "branch");

frappe.ui.form.on('Range', {
	refresh: function(frm) {

	}
});
