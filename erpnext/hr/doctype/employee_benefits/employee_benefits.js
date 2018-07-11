// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Benefits', {
	refresh: function(frm) {
		cur_frm.add_custom_button(__('Bank Entries'), function() {
			frappe.route_options = {
				"Journal Entry Account.reference_type": me.frm.doc.doctype,
				"Journal Entry Account.reference_name": me.frm.doc.name,
			};
			frappe.set_route("List", "Journal Entry");
		}, __("View"));

	},
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			cur_frm.set_value("posting_date", get_today())
		}
	}
});
