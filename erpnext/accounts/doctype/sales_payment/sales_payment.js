// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("cost_center", "branch", "branch");
frappe.ui.form.on('Sales Payment', {
	refresh: function(frm) {

	},
	setup: function(frm){
                frm.get_field('references').grid.editable_fields = [
                        {fieldname: 'reference_name', columns: 2},
                        {fieldname: 'total_amount', columns: 2},
                        {fieldname: 'posting_date', columns: 3},
                        {fieldname: 'outstanding_amount', columns: 3}
                ];

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
        },
	"get_invoices": function(frm) {
                if(frm.doc.cost_center && frm.doc.party) {
                        return frappe.call({
                                method: "get_invoices",
                                doc: frm.doc,
                                callback: function(r, rt) {
                                        frm.refresh_field("items");
                                        frm.refresh_fields();
                                }
                        });
                }
        },

});
