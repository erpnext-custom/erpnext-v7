// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['EME Payment'] = {
	add_fields: ["docstatus", "workflow_state"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		console.log("testing")
		if(doc.docstatus==0) {
			if(doc.workflow_state == "Rejected") {
				return ["Rejected", "red", "workflow_state,like,Rejected"];
			}
			else if(doc.workflow_state == "Payment Pending") {
				return ["Paid", "orange", "workflow_state,like,Payment Pending"];
			}
		}
		if(doc.docstatus == 1) {
			return ["Paid", "green"];
		}
	}
};
