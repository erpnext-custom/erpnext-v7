// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Sub Group', {
	refresh: function(frm) {

	},
	// NRDCLTTPL Begins, added by SHIV on 2019/12/01
	is_crm_item: function(frm){
		cur_frm.toggle_reqd("uom", frm.doc.is_crm_item);
	}
	// NRDCLTTPL
});
