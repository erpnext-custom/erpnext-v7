// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Modifier', {
	refresh: function(frm) {

	},
	onload: function(frm){
		frm.toggle_display("party_type", 0);
		frm.refresh_field('party_type');
		frm.toggle_display("party", 0);
		frm.refresh_field('party');
	},
	"credit_account": function(frm){
		frappe.model.get_value('Account', { 'name': frm.doc.credit_account }, 'account_type',
		function (r) {
			if (r.account_type == 'Receivable' || r.account_type == 'Payable'){
				frm.toggle_display("party_type", 1);
				frm.refresh_field('party_type');
				frm.toggle_display("party", 1);
				frm.refresh_field('party');
			}else{
				frm.toggle_display("party_type", 0);
				frm.refresh_field('party_type');
				frm.toggle_display("party", 0);
				frm.refresh_field('party');
			}
		});
		
	}
});
frappe.ui.form.on("Asset Modifier Item", {
	"amount": function(frm, cdt, cdn) {
		calculate_value(frm, cdt, cdn)
	},
	});
function calculate_value(frm, cdt, cdn) {
	var total_amount = 0;
	frm.doc.items.forEach(function(d) {
		if(d.amount) { 
			total_amount += d.amount
		}
	
	})
	frm.set_value("value", total_amount)
	cur_frm.refresh_field("value")

}

cur_frm.add_fetch("asset", "asset_account", "asset_account");
cur_frm.add_fetch("asset", "credit_account", "credit_account");

