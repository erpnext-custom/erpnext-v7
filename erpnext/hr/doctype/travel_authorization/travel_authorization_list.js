// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Travel Authorization'] = {
	add_fields: ["employee_name", "employee", "grade", "docstatus", "document_status"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if(doc.docstatus==0) {
			if(doc.document_status == 'Rejected') {
				return ["Authorization Rejected", "red", "document_status,=,Rejected"];
			}
			else {
				return ["Authorization Draft", "orange", "docstatus,=,0"];
			}
		}

		if(doc.docstatus == 1) {
			return ["Approved", "green", "docstatus,=,1"];
		}
	}
};
