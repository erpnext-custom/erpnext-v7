// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Load Request Editor', {
	refresh: function(frm) {

	},
	get_queue: function(frm){
		frappe.call({
			method:"get_queue",
			doc: frm.doc,
			callback: function(r){
				frm.refresh_fields();
			}
		})
	}
});
