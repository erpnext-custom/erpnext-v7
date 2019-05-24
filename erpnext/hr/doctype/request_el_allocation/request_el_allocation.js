// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Request EL Allocation', {
	refresh: function(frm) {
		 if(frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Rejected"){
                        frm.set_df_property("approver", "hidden", 1);
                        frm.set_df_property("approver_name", "hidden", 1);
                }
	},
	onload: function(frm) {
		frm.set_query("employee", function() {
                        return {
                                        "filters": {"status": "Active"}
                        }
                });

	}
});
