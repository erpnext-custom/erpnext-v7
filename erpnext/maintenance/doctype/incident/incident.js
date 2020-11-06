// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Incident', {
	refresh: function(frm) {

	},

	onload: function(frm) {
		if (!frm.doc.posting_date) {
			cur_frm.set_value("posting_date", get_today())
		}
	}
});
