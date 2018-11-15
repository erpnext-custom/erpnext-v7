// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Grade', {
	refresh: function(frm) {

	},
	increment: function(frm) {
		if(frm.doc.increment > 0 && frm.doc.increment_percent > 0) {
			frm.set_value("increment", 0)
			frappe.msgprint("Can not have both lumpsum and percent for increment")
		}
	},
	increment_percent: function(frm) {
		if(frm.doc.increment > 0 && frm.doc.increment_percent > 0) {
			frm.set_value("increment_percent", 0)
			frappe.msgprint("Can not have both lumpsum and percent for increment")
		}
	}
});
cur_frm.fields_dict['employee_subgroup'].get_query = function(doc, dt, dn) {
	return {
		filters:{"employee_group": doc.employee_group}
	}
}
