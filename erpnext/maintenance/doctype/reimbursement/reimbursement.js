// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "cost_center", "cost_center")
frappe.ui.form.on('Reimbursement', {
	refresh: function(frm) {

	},
	purpose: function(frm){
		if(frm.doc.purpose == 'Hiring/Transportation'){
		frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Maintenance Accounts Settings",
					fieldname: "hire_expense_account",
				},
				callback: function (r) {
					if (r.message) {
						cur_frm.set_value("expense_account", r.message.hire_expense_account);
						refresh_field('expense_account');
					}
				}
			});
		}
		else if(frm.doc.purpose == 'POL'){
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Maintenance Accounts Settings',
					fieldname: "pol_advance_account"
				},
				callback: function (r) {
					if (r.message) {
						cur_frm.set_value("expense_account", r.message.pol_advance_account);
						refresh_field('expense_account');
					}
				}
			});
		}
	}
});
