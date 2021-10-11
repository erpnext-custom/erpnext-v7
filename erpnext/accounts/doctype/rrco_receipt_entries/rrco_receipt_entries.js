// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('RRCO Receipt Entries', {
	refresh: function(frm) {

	},
	get_detail: function(frm) {
		return frappe.call({
		method: "erpnext.accounts.doctype.rrco_receipt_entries.rrco_receipt_entries.get_detail",
		args: {
			branch: frm.doc.branch
		},
		callback: function(r) {
			if(r.message) {
				console.log("test")
			}
		}
		});
	}
});
