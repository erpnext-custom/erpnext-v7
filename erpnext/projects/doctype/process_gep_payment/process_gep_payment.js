// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("project", "branch", "branch")

frappe.ui.form.on('Process GEP Payment', {
	refresh: function(frm) {
		if(!frm.doc.from_date) {
			frm.set_value("from_date", frappe.datetime.month_start(get_today()))	
		}
		if(!frm.doc.to_date) {
			frm.set_value("to_date", frappe.datetime.month_end(get_today()))	
		}
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())	
		}

	},
	
	load_entries: function(frm) {
		frappe.msgprint("Loading....")
	}
});
