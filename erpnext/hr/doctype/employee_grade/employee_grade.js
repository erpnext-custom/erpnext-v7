// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Grade', {
	refresh: function(frm) {

	}
});
cur_frm.fields_dict['employee_subgroup'].get_query = function(doc, dt, dn) {
	return {
		filters:{"employee_group": doc.employee_group}
	}
}
