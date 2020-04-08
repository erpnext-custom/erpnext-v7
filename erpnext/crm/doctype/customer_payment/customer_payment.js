// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('customer_order', 'user', 'user');
cur_frm.add_fetch('customer_order', 'site', 'site');
cur_frm.add_fetch('customer_order', 'customer', 'customer');
cur_frm.add_fetch('customer_order', 'sales_order', 'sales_order');
cur_frm.add_fetch('customer_order', 'total_payable_amount', 'total_payable_amount');
cur_frm.add_fetch('customer_order', 'total_paid_amount', 'total_paid_amount');
cur_frm.add_fetch('customer_order', 'total_balance_amount', 'total_balance_amount');
cur_frm.add_fetch('customer_order', 'total_balance_amount', 'paid_amount');
frappe.ui.form.on('Customer Payment', {
	setup: function(frm){
		frm.set_query("paid_to", function() {
			var account_types = ["Bank"]

			return {
				filters: {
					"account_type": ["in", account_types],
					"is_group": 0,
				}
			}
		});
	},
	onload: function(frm){
		cur_frm.set_query("customer_order", function(){
			return {
				"filters": [
					["docstatus", "!=", "2"],
				]
			}
		});
	},
	refresh: function(frm) {

	},
	mode_of_payment: function(frm){
		cur_frm.toggle_reqd(["reference_no", "reference_date", "paid_to"], frm.doc.mode_of_payment == "Cheque Payment");
	},
	pay_now: function(frm){
		submit_order(frm);
	},
	approval_status: function(frm){
		cur_frm.toggle_reqd("rejection_reason",(frm.doc.approval_status=="Rejected") ? 1 : 0);
	},
});

var submit_order = function(frm){
	//frm.save();
	frappe.call({
		"method": "submit_customer_payment",
		doc: frm.doc,
		callback: function(r, rt){
			cur_frm.refresh();
		}
	});
}
