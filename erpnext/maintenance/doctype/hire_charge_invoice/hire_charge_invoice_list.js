// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// render
frappe.listview_settings['Hire Charge Invoice'] = {
	add_fields: ["invoice_jv", "docstatus", "payment_jv"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
		if(doc.docstatus==0) {
				return ["Invoice Created", "grey", "docstatus,=,0"];
		}

		if(doc.docstatus == 1) {
			if(doc.invoice_jv && doc.payment_jv) {
				return ["Payment Completed", "green", "docstatus,=,1|invoice_jv,>,0|payment_jv,>,0"];
			}
			else {
				return ["Invoice Raised", "blue", "docstatus,=,1|invoice_jv,>,0"];
			}
		}
		
		if(doc.docstatus == 2) {
			return ["Invoice Cancelled", "red", "docstatus,=,2"]
		}
	}
};
