// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Officiating Employee', {
	refresh: function(frm) {
		if(frm.doc.to_date < get_today) {
			console.log("SHOW")
			cur_frm.add_custom_button(__('Revoke Permissions'), this.revoke_permission)
			frm.add_custom_button("Create Job Card", function() {
				frappe.call({
					method: "erpnext.hr.doctype.officiating_employee.officiating_employee.revoke_perm",
					args: {frm: cur_frm},
					callback: function(r) {}
				})
			});
		}
	},
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			frm.set_value("posting_date", get_today())
		}
	},
	validate: function(frm) {
		if(frm.doc.employee) {
			return frappe.call({
				method: "validate",
				doc: frm.doc,
				callback: function(r, rt) {
					frm.refresh_field("items");
					frm.refresh_fields();
				}
			});
		}
	},
	"revoke_permission": function(frm) {
		console.log("INSIS")
		frappe.call({
			method: "erpnext.hr.doctype.officiating_employee.officiating_employee.revoke_perm",
			args: {frm: cur_frm},
			callback: function(r, rt) {
			}
		})	
	}
});

cur_frm.add_fetch("employee", "employee_name", "employee_name")
cur_frm.add_fetch("officiate", "employee_name", "officiate_name")



