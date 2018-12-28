// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['HSD Payment'] = {
	add_fields: ["docstatus"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if(doc.docstatus==0) {
			return ["Payment Created", "grey", "docstatus,=,0"];
		}

		if(doc.docstatus == 1) {
			return ["Payment Completed", "green", "docstatus,=,1"];
		}
	}
};
