// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Mechanical Payment'] = {
	add_fields: ["docstatus"],
	get_indicator: function(doc) {
		if(doc.docstatus == 1) {
			return ["Payment Received", "green", "docstatus,=,1"];
		}
	}
};
