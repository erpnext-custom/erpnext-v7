// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transporter Trip Log', {
	setup: function(frm) {
		frm.get_docfield("item").allow_bulk_edit = 1;
	}
});
