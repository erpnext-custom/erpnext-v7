// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Asset Modifier', {
	refresh: function(frm) {

	},
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

