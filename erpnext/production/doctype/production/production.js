// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch("item_code", "item_name", "item_name")
cur_frm.add_fetch("item_code", "stock_uom", "uom")
cur_frm.add_fetch("price_template", "rate_amount", "cop")

frappe.ui.form.on('Production', {
	onload: function(frm) {
                if (!frm.doc.posting_date) {
                        frm.set_value("posting_date", get_today());
                }
	},

	refresh: function(frm) {

	}
});
