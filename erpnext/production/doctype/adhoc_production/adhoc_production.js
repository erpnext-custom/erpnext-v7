// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("location", "branch", "branch")
cur_frm.add_fetch("location", "company", "company")

frappe.ui.form.on('Adhoc Production', {
	refresh: function(frm) {

	}
});
