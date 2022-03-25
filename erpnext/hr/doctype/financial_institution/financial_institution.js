// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Financial Institution', {
	setup: function(frm) {
		frm.get_docfield("items").allow_bulk_edit = 1;		
	},
	refresh: function(frm) {
		cur_frm.set_query("bank_branch", function(){
			return {
				"filters": [
					["financial_institution", "=", frm.doc.account_bank_name],					
				]
			}
		});
	}
});
