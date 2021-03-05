// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('RRCO Receipt Tool', {
	refresh: function(frm) {

	},
	get_invoices: function(frm) {
		return frappe.call({
			method: "get_invoices",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("item");
				frm.refresh_fields();
			},
			freeze: true,
			freeze_message: "Loading Payment Invoices..... Please Wait"
		});
	}
});
