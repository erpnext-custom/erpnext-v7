// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consolidation Adjustment Entry', {
	refresh: function(frm) {
		frm.get_docfield("items").allow_bulk_edit = 1;
	}
});
