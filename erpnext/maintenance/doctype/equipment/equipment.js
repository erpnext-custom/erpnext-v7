// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment', {
	refresh: function(frm) {

	},
	validate: function(frm) {
		if (frm.doc.operators) {
			frm.doc.operators.forEach(function(d) { 
				frm.set_value("current_operator", d.operator)
			})
			frm.refresh_field("current_operator")
		}
	}
});

