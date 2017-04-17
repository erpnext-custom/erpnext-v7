// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transfer CoGM', {
	refresh: function(frm) {
	},

	from_fiscal_year: function(frm) {
		if(frm.doc.from_fiscal_year && frm.doc.from_account) {
			frappe.call({
				method: 'erpnext.accounts.doctype.transfer_cogm.transfer_cogm.calculate_amount',
				args: {
					fiscal_year: frm.doc.from_fiscal_year,
					account: frm.doc.from_account
				},
				callback: function(r) {
					if(r.message) {
						frm.set_value("amount", r.message.toString())
					}	
				}
			})
		}
	}
});
