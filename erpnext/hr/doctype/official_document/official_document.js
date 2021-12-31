// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
cur_frm.add_fetch("employee", "employee_subgroup", "grade")
cur_frm.add_fetch("employee", "designation", "designation")
cur_frm.add_fetch("employee", "branch", "branch")
cur_frm.add_fetch("document_type", 'letter_index', 'letter_index')

frappe.ui.form.on('Official Document', {
	refresh: function(frm) {

		if (!frm.doc.date){
			cur_frm.set_value("date", get_today())
		}




	},

	approval: function(frm) {
		if(frm.doc.approval){
			frm.set_value("approval_name", frappe.user.full_name(frm.doc.approval));
		}
	},

	verified_by: function(frm) {
		if (frm.doc.verified_by){
			frm.set_value("verified_name", frappe.user.full_name(frm.doc.verified_by));
		}
	},

});
