// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch("branch", "expense_bank_account", "credit_account")

frappe.ui.form.on('Transporter Payment', {
	setup: function(frm) {
		frm.get_field('items').grid.editable_fields = [
			{fieldname: 'posting_date', columns: 2},
			{fieldname: 'item_code', columns: 2},
			{fieldname: 'transportation_amount', columns: 2},
			{fieldname: 'unloading_amount', columns: 2},
			{fieldname: 'total_amount', columns: 2},
		];
		frm.get_field('pols').grid.editable_fields = [
			{fieldname: 'posting_date', columns: 2},
			{fieldname: 'item_code', columns: 2},
			{fieldname: 'qty', columns: 2},
			{fieldname: 'rate', columns: 2},
			{fieldname: 'amount', columns: 2},
		];
	},
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			cur_frm.set_value("posting_date", get_today())
		}
		frm.set_query("credit_account", function() {
			return {
				filters: {
					is_group: 0
				}
			}
		})
		frm.set_query("equipment", function() {
			return {
				filters: {
					is_disabled: 0
				}
			}
		})
	},

	refresh: function(frm) {
                if(frm.doc.docstatus===1){
                        frm.add_custom_button(__('Accounting Ledger'), function(){
                                frappe.route_options = {
                                        voucher_no: frm.doc.name,
                                        from_date: frm.doc.posting_date,
                                        to_date: frm.doc.posting_date,
                                        company: frm.doc.company,
                                        group_by_voucher: false
                                };
                                frappe.set_route("query-report", "General Ledger");
                        }, __("View"));
                }

	},

	get_details: function(frm) {
		return frappe.call({
			method: "get_payment_details",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_fields();
			},
			freeze: true,
			freeze_message: "Loading Payment Details..... Please Wait"
		})
	}
});




