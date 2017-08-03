// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Muster Roll Employee', {
	refresh: function(frm) {

	},
	rate_per_day: function(frm) {
		if(frm.doc.rate_per_day) {
			frm.set_value("rate_per_hour", (frm.doc.rate_per_day * 1.5) / 8)
			frm.refresh_field("rate_per_hour")
		}
	}
});


