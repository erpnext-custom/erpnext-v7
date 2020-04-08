// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('BFS Settings', {
	setup: function(frm){
		frm.get_docfield("mobile_rc").allow_bulk_edit = 1;
		frm.get_docfield("web_rc").allow_bulk_edit = 1;

		frm.get_field('mobile_rc').grid.editable_fields = [
			{fieldname: 'response_code', columns: 2},
			{fieldname: 'response_desc', columns: 8},
		];
		frm.get_field('web_rc').grid.editable_fields = [
			{fieldname: 'response_code', columns: 2},
			{fieldname: 'response_desc', columns: 8},
		];
	},
	refresh: function(frm) {

	}
});
