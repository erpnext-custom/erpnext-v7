// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("cost_center", "branch", "branch")
cur_frm.add_fetch("project", "cost_center", "cost_center")
cur_frm.add_fetch("project", "branch", "branch")

frappe.ui.form.on('Muster Roll Employee', {
	refresh: function(frm) {

	},

	rate_per_day: function(frm) {
		if(frm.doc.rate_per_day) {
			frm.set_value("rate_per_hour", (frm.doc.rate_per_day * 1.5) / 8)
			frm.refresh_field("rate_per_hour")
		}
	},

	"status": function(frm) {
		cur_frm.toggle_reqd("separation_date", frm.doc.status == "Left")
	}

});


