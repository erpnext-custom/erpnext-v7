// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Travel Authorization'] = {
	add_fields: ["employee_name", "employee", "grade", "docstatus", "document_status"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		/*
		console.log(doc.docstatus+' : '+doc.document_status);
		if(doc.docstatus==0) {
			if(doc.document_status == 'Rejected') {
				return ["Authorization Rejected", "red", "document_status,=,Rejected"];
			}
			else {
				return ["Authorization Draft", "orange", "docstatus,=,0|document_status,not like,Rejected"];
			}
		}
		*/

		/*
		if(doc.docstatus==2 && doc.document_status == 'Rejected'){
			return ["Authorization Rejected", "red", "document_status,=,Rejected"];
		}
		*/
		
		if(doc.docstatus == 1) {
			if(doc.document_status == 'Rejected'){
				return ["Authorization Rejected", "red", "document_status,=,Rejected"];
			}
			else {
				return ["Approved", "green", "docstatus,=,1"];
			}
		}
		
		if(doc.docstatus == 0) {
				return ["Authorization Draft", "orange", "docstatus,=,0|document_status,not like,Rejected"];
		}
	}
};
