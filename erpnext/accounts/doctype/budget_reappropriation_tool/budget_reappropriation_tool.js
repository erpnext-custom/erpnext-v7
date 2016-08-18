// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget Reappropriation Tool', {
	refresh: function(frm) {

	},

	refresh: function(frm) {
		frm.disable_save();
	},

	reappropriate_button: function(frm) {
		if(frm.doc.from_cost_center && frm.doc.to_cost_center && frm.doc.from_account && frm.doc.to_account && frm.doc.amount) { 
			frappe.call({
				method: "erpnext.accounts.doctype.budget_reappropriation_tool.budget_reappropriation_tool.reappropriate",
				args: {
					"from_cc": frm.doc.from_cost_center,
					"to_cc": frm.doc.to_cost_center,
					"from_acc": frm.doc.from_account,
					"to_acc": frm.doc.to_account,
					"amount": frm.doc.amount
				},
				callback: function(r) {
				
				}
			});
		}
		else if(frm.doc.amount <= 0) {
			msgprint("Amount should be greater than 0")
		}
		else {
			msgprint("Fill all fields before submitting")
		}
	}
});
