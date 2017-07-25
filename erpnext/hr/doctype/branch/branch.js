// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Branch', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		frm.set_query("cost_center", function() {
			return {
				filters: {
					company: frm.doc.company,
					is_disabled: 0,
				}
			}
		})
	}
});
