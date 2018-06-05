// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("employee", "user_id", "user")
cur_frm.add_fetch("employee", "branch", "current_branch")

frappe.ui.form.on('Assign Branch', {
	refresh: function(frm) {

	},
	get_all_branch: function(frm) {
		//load_accounts(frm.doc.company)
		return frappe.call({
			method: "get_all_branches",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			}
		});
	}
});

cur_frm.fields_dict['employee'].get_query = function(doc, dt, dn) {
       return {
               filters:{"status": "Active"}
       }
}

