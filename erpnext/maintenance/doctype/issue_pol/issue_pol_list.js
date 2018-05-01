// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Issue POL'] = {
	add_fields: ["docstatus"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if(doc.docstatus==0) {
			return ["Issue POL Created", "grey", "docstatus,=,0"];
		}

		if(doc.docstatus == 1) {
			return ["POL Issued", "green", "docstatus,=,1"];
		}
	}
};
