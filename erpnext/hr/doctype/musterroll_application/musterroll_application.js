// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("project", "cost_center", "cost_center")
cur_frm.add_fetch("cost_center", "branch", "branch")

frappe.ui.form.on('MusterRoll Application', {
	refresh: function(frm) {

	},
	onload: function(frm) {
		if (!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today());
		}
		frm.set_query("approver", function() {
			return {
				query: "erpnext.hr.doctype.leave_application.leave_application.get_approvers",
				filters: {
					employee: frm.doc.requested_by
				}
			};
		}); 
	}
});

frappe.ui.form.on('MusterRoll Application Item', {
	"rate_per_day": function(frm, cdt, cdn) {
		doc = locals[cdt][cdn]
		if(doc.rate_per_day) {
			frappe.model.set_value(cdt, cdn, "rate_per_hour", (doc.rate_per_day * 1.5) / 8)
			cur_frm.refresh_field("rate_per_hour")
		}
	}
})

