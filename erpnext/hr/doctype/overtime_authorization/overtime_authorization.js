// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "employee_name", "employee_name");
cur_frm.add_fetch("employee", "branch", "branch");
cur_frm.add_fetch("employee", "designation", "designation");
cur_frm.add_fetch("employee", "employee_subgroup", "grade");

frappe.ui.form.on('Overtime Authorization', {
	refresh: function(frm) {
		if (frm.doc.docstatus == 1 && !frm.doc.overtime_claim) {
			frm.add_custom_button("Overtime Claim", function() {
				frappe.model.open_mapped_doc({
					method: "erpnext.hr.doctype.overtime_authorization.overtime_authorization.make_overtime_claim",
					frm: cur_frm
				})
			}, __("Make"));
		}
	}
});
