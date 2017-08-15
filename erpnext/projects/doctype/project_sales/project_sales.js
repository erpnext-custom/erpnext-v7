// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("selling_project", "cost_center", "selling_cost_center")
cur_frm.add_fetch("selling_project", "branch", "selling_branch")
cur_frm.add_fetch("buying_project", "cost_center", "buying_cost_center")
cur_frm.add_fetch("buying_project", "branch", "buying_branch")
cur_frm.add_fetch("item_code", "item_name", "item_name")
cur_frm.add_fetch("item_code", "expense_account", "expense_account")

frappe.ui.form.on('Project Sales', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on('Project Sales Item', {
	rate: function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	},
	qty: function(frm, cdt, cdn) {
		calculate_amount(frm, cdt, cdn)
	}
});

function calculate_amount(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	if (item.rate && item.qty) {
		frappe.model.set_value(cdt, cdn, "amount", item.rate * item.qty)
	}
	cur_frm.refresh_fields("amount")
}
