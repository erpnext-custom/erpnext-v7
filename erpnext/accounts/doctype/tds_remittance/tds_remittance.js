// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('TDS Remittance', {
	get_details: function(frm) {
		
		return frappe.call({
			method: "get_details",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("items");
				frm.refresh_fields();
			}
		});
	},
	refresh: function(frm) {

	},
	tds_rate: function(frm){
		if (frm.doc.tds_rate =2){
			 frappe.model.get_value('Accounts Settings',{'name': 'Accounts Settings'},  'tds_2_account',
                        function(d) {
                            cur_frm.set_value("tds_account",d.tds_2_account);
	
                        });
			}
	}
});
