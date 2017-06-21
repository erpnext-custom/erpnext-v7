// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Budget', {
	onload: function(frm) {
		frm.set_query("cost_center", function() {
			return {
				filters: {
					company: frm.doc.company
				}
			}
		})

		frm.set_query("account", "accounts", function() {
			return {
				filters: {
					company: frm.doc.company,
			//		report_type: "Profit and Loss",
					is_group: 0
				}
			}
		})

		frm.set_query("monthly_distribution", function() {
			return {
				filters: {
					fiscal_year: frm.doc.fiscal_year
				}
			}
		})
	}
});

//Custom Scripts
//Calculate when initial budget changes
frappe.ui.form.on("Budget Account", "initial_budget", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//Calculate when supplementary budget changes
frappe.ui.form.on("Budget Account", "supplementary_budget", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//Calculate when re-appropiation budget received budget changes
frappe.ui.form.on("Budget Account", "budget_received", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//Calculate when re-appropiation budget sent budget changes
frappe.ui.form.on("Budget Account", "budget_sent", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//recalculate during validate
frappe.ui.form.on("Budget Account", "validate", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//Function to calculate available budget (budget_amount)
function calculate_budget_amount(child) {
    return (child.initial_budget + (child.supplementary_budget || 0) + (child.budget_received || 0)  - (child.budget_sent || 0) )
}

//custom Scripts
//Calculate when initial budget changes
frappe.ui.form.on("Budget Account", "initial_budget", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//Calculate when supplementary budget changes
frappe.ui.form.on("Budget Account", "supplementary_budget", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//Calculate when re-appropiation budget received budget changes
frappe.ui.form.on("Budget Account", "budget_received", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//Calculate when re-appropiation budget sent budget changes
frappe.ui.form.on("Budget Account", "budget_sent", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//recalculate during validate
frappe.ui.form.on("Budget Account", "validate", function(frm, cdt, cdn) {
    var child = locals[cdt][cdn];

    frappe.model.set_value(cdt, cdn, "budget_amount", calculate_budget_amount(child));
});

//Function to calculate available budget (budget_amount)
function calculate_budget_amount(child) {
    return (child.initial_budget + (child.supplementary_budget || 0) + (child.budget_received || 0)  - (child.budget_sent || 0) )
}
