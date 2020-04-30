// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Online Payment', {
	refresh: function(frm) {
		cur_frm.set_df_property("status", "read_only", frm.doc.status=="Successful");
	}
});
