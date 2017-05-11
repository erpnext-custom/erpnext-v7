// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Travel Claim'] = {
	add_fields: ["employee_name", "employee", "grade", "balance_amount", "supervisor_approval", "docstatus"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if(doc.docstatus==0) {
			if(doc.claim_status != '') {
				return ["Claim Rejected", "red", "claim_status,=,1"];
			}
			else if(doc.supervisor_approval==1) {
				return ["Supervisor Approved", "blue", "supervisor_approval,=,1"];
			}
			else {
				return ["Claim Draft", "orange", "docstatus,=,0"];
			}
		}

		if(doc.docstatus == 1) {
				return ["Claim Approved", "green", "docstatus,=,1"];
		}
	}
};
