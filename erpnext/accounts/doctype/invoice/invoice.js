// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("cost_center", "branch", "branch");

frappe.ui.form.on('Invoice', {
	setup: function(frm){
                frm.get_field('items').grid.editable_fields = [
                        {fieldname: 'item', columns: 2},
                        {fieldname: 'item_name', columns: 3},
                        {fieldname: 'qty', columns: 1},
                        {fieldname: 'rate', columns: 2},
			{fieldname: 'amount', columns: 2}
                ];
        },

	"discount_amount": function(frm) {
		frm_set		

	},
	"refresh": function(frm){
		if(frm.doc.docstatus == 1) {
                        cur_frm.add_custom_button(__('Accounting Ledger'), function() {
                                frappe.route_options = {
                                        voucher_no: frm.doc.name,
                                        from_date: frm.doc.posting_date,
                                        to_date: frm.doc.posting_date,
                                        company: frm.doc.company,
                                        group_by_voucher: false
                                };
                                frappe.set_route("query-report", "General Ledger");
                        }, __("View"));
		//cur_frm.add_custom_button(__('Payment'), cur_frm.cscript.make_payment_entry, __("Make"));
                }
	}
});

frappe.ui.form.on("Invoice Item", {
        "qty": function(frm, cdt, cdn) {
		var item  = locals[cdt][cdn]
                if(item.rate) {
			calculate_amount(frm, cdt, cdn)
		}
        },
        "rate": function(frm, cdt, cdn) {
		var item = locals[cdt][cdn]
		if(item.qty) {
                	calculate_amount(frm, cdt, cdn)
		}
        },
	"item": function(frm, cdt, cdn) {
		msgprint("this is printed");
		var item = locals[cdt][cdn]
		frm.add_fetch("item", "income_account", "income_account");
		}
});

function calculate_amount(frm, cdt, cdn) {
	var item = locals[cdt][cdn]
	frappe.model.set_value(cdt, cdn, "amount", parseFloat(item.qty) * parseFloat(item.rate)) 
}
