// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('RRCO Receipt Tool', {
	refresh: function(frm) {

	},
	purpose: function(frm) {
		if(frm.doc.purpose == "Leave Encashment" || frm.doc.purpose == "Purchase Invoices")
		{	
			cur_frm.set_df_property("to_date", "reqd", 1);
			cur_frm.set_df_property("from_date", "reqd", 1);
		}else{
			cur_frm.set_df_property("to_date", "reqd", 0);
			cur_frm.set_df_property("from_date", "reqd", 0);
		}
	},
	get_invoices: function(frm) {
		return frappe.call({
			method: "get_invoices",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("item");
				frm.refresh_fields();
			},
			freeze: true,
			freeze_message: "Loading Payment Invoices..... Please Wait"
		});
	}
});
