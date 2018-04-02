// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("project", "cost_center", "cost_center")
cur_frm.add_fetch("cost_center", "branch", "branch")

frappe.ui.form.on('MusterRoll Application', {
	setup: function(frm) {
		frm.get_docfield("items").allow_bulk_edit = 1;
	},
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
	},
	get_employees: function(frm) {
		//load_accounts(frm.doc.company)
		return frappe.call({
			method: "get_employees",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			}
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
	},
	"existing_cid": function(frm, cdt, cdn){
		var child  = locals[cdt][cdn];

		frappe.call({
			method: "frappe.client.get_value",
			args: {doctype: "Muster Roll Employee", fieldname: ["person_name", "rate_per_day", "rate_per_hour"],
					filters: {
								name: child.existing_cid
					}},
			callback: function(r){
				frappe.model.set_value(cdt, cdn, "person_name", r.message.person_name);
				frappe.model.set_value(cdt, cdn, "rate_per_day", r.message.rate_per_day);
				frappe.model.set_value(cdt, cdn, "rate_per_hour", r.message.rate_per_hour);
			}
		})
	},	
})
