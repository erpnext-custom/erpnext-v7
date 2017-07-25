// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Job Card'] = {
	add_fields: ["payment_jv", "docstatus", "assigned_to"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if(doc.docstatus==0) {
			if(doc.assigned_to) {
				return ["Job Assigned", "orange", "docstatus,=,0|assigned_to,not like, "];
			}
			else {			
				return ["Job Created", "grey", "docstatus,=,0|assigned_to,like, "];
			}
		}

		if(doc.docstatus == 1) {
			if(doc.payment_jv) {
				return ["Payment Received", "green", "docstatus,=,1|payment_jv,>,0"];
			}
			else {
				return ["Payment Booked", "blue", "docstatus,=,1|payment_jv,<=,0"];
			}
		}
	}
};
