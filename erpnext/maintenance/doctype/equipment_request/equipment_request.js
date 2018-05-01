// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Equipment Request', {
	refresh: function(frm) {
		if (frm.doc.docstatus == 1) {
                        frm.add_custom_button("Create Equipment Hiring Form", function() {
                                frappe.model.open_mapped_doc({
                                        method: "erpnext.maintenance.doctype.equipment_request.equipment_request.make_hire_form",
                                        frm: cur_frm
                                })
                        });
                }
	}
});
