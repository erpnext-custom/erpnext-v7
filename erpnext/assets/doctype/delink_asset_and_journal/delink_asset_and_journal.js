// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("asset", "asset_name", "asset_name")

frappe.ui.form.on('Delink asset and journal', {
	refresh: function(frm) {

	}
});
