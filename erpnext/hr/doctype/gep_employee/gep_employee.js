// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("cost_center", "branch", "branch")
cur_frm.add_fetch("project", "cost_center", "cost_center")
cur_frm.add_fetch("project", "branch", "branch")

frappe.ui.form.on('GEP Employee', {
	onload: function(frm) {
		if(!frm.doc.date_of_joining) {
			cur_frm.set_value("date_of_joining", get_today())
		}	
	},
	salary: function(frm) {
		cur_frm.set_value("ot_amount", ((frm.doc.salary * 1.5)/ (30 * 8)))
	},
	"status": function(frm) {
		cur_frm.toggle_reqd("date_of_separation", frm.doc.status == "Left")
	}
});
